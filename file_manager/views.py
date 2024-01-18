from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db.models import Q
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.response import Response

from file_manager.mixins.views import (
    CustomCreateModelMixin,
    PersonalMixin,
    SharedWithMeMixin,
    ShareModelMixin,
    UnshareModelMixin,
)

from .models import File, Folder, Share
from .permissions import (
    CanDelete,
    CanEdit,
    CanEditParentFolder,
    CanRead,
    CanShare,
    IsOwner,
)
from .serializers import FolderSerializer, ShareSerializer


class FolderViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
    # Custom Mixins,
    CustomCreateModelMixin,
    ShareModelMixin,
    UnshareModelMixin,
    SharedWithMeMixin,
    PersonalMixin,
):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer

    def get_serializer(self, *args, **kwargs):
        if self.action == "share":
            return ShareSerializer(*args, **kwargs)
        return super().get_serializer(*args, **kwargs)

    def get_permissions(self):
        if self.action == "retrieve":
            permission_classes = [IsOwner | CanRead]
        elif self.action in ["update", "partial_update"]:
            permission_classes = [IsOwner | CanEdit]
        elif self.action in ["share", "unshare"]:
            permission_classes = [IsOwner | CanShare]
        elif self.action == "destroy":
            permission_classes = [IsOwner | CanDelete]
        else:  # create
            permission_classes = [CanEditParentFolder]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user

        if self.action == "personal_folders":
            return Folder.objects.filter(owner=user)

        elif self.action == "shared_with_me":
            folder_content_type = ContentType.objects.get_for_model(Folder)
            shared_folders_ids = Share.objects.filter(
                shared_with=user, content_type=folder_content_type, can_read=True
            ).values_list("object_id", flat=True)
            return Folder.objects.filter(id__in=shared_folders_ids)

        elif self.action == "retrieve":
            folder_content_type = ContentType.objects.get_for_model(Folder)
            shared_folders_ids = Share.objects.filter(
                shared_with=user, content_type=folder_content_type, can_read=True
            ).values_list("object_id", flat=True)
            return Folder.objects.filter(Q(owner=user) | Q(id__in=shared_folders_ids))

        return super().get_queryset()
