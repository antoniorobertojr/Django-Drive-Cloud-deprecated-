from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from rest_framework import mixins, serializers, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from .mixins import (PersonalMixin, SharedWithMeMixin, ShareModelMixin,
                     UnshareModelMixin)
from .models import Folder, Share
from .permissions import (CurrentUserCanDelete, CurrentUserCanEdit,
                          CurrentUserCanRead, CurrentUserCanShare, IsOwner)
from .serializers import FolderSerializer, ShareFolderSerializer


class FolderViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet,
                   # Custom Mixins
                   ShareModelMixin,
                   UnshareModelMixin,
                   SharedWithMeMixin,
                   PersonalMixin):

    queryset = Folder.objects.all()
    serializer_class = FolderSerializer

    def get_serializer(self, *args, **kwargs):
        if self.action == 'share':
            return ShareFolderSerializer(*args, **kwargs)
        return super().get_serializer(*args, **kwargs)

    def get_permissions(self):
        if self.action == "retrieve":
            permission_classes = [IsOwner | CurrentUserCanRead]
        elif self.action in ["update", "partial_update"]:
            permission_classes = [IsOwner | CurrentUserCanEdit]
        elif self.action in ["share", "unshare"]:
            permission_classes = [IsOwner | CurrentUserCanShare]
        elif self.action == "destroy":
            permission_classes = [IsOwner | CurrentUserCanDelete]
        else: # create
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user

        if self.action == 'personal_folders':
            return Folder.objects.filter(owner=user)

        elif self.action == 'shared_with_me':
            folder_content_type = ContentType.objects.get_for_model(Folder)
            shared_folders_ids = Share.objects.filter(
                shared_with=user, 
                content_type=folder_content_type,
                can_read=True
            ).values_list('object_id', flat=True)
            return Folder.objects.filter(id__in=shared_folders_ids)

        elif self.action == 'retrieve':
            folder_content_type = ContentType.objects.get_for_model(Folder)
            shared_folders_ids = Share.objects.filter(
                shared_with=user, 
                content_type=folder_content_type,
                can_read=True
            ).values_list('object_id', flat=True)
            return Folder.objects.filter(Q(owner=user) | Q(id__in=shared_folders_ids))

        return super().get_queryset()

    def perform_create(self, serializer):
        user = self.request.user
        parent_id = serializer.validated_data.get('parent')
        if parent_id:
            try:
                parent_folder = Folder.objects.get(pk=parent_id)
            except Folder.DoesNotExist:
                raise serializers.ValidationError("Parent folder does not exist.")

            if parent_folder.owner != user:
                folder_content_type = ContentType.objects.get_for_model(Folder)

                try:
                    share = Share.objects.get(
                        shared_with=user,
                        content_type=folder_content_type,
                        object_id=parent_id,
                        can_edit=True
                    )
                except Share.DoesNotExist:
                    raise PermissionDenied("You do not have permission to create a folder in this location.")

        try:
            serializer.save(owner=user)
        except Exception as e:
            raise serializers.ValidationError({"detail": str(e)})
