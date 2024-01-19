from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, viewsets
from rest_framework.decorators import action

from file_manager.mixins.views import (CustomCreateModelMixin,
                                       FileDownloadMixin, PersonalMixin,
                                       SharedWithMeMixin, ShareModelMixin,
                                       UnshareModelMixin)

from .models import File, Folder, Share
from .permissions import (CanDelete, CanEdit, CanEditParentFolder, CanRead,
                          CanShare, IsOwner)
from .serializers import (FileSerializer, FolderSerializer, ShareSerializer,
                          UnshareSerializer)


class BaseViewSet(
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
    model = None

    def get_serializer(self, *args, **kwargs):
        if self.action == "share":
            return ShareSerializer(*args, **kwargs)
        elif self.action == "unshare":
            return UnshareSerializer(*args, **kwargs)
        return super().get_serializer(*args, **kwargs)

    def get_permissions(self):
        print(self.action)
        if self.action in ["retrieve", "download", "personal", "shared_with_me"]:
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

        if self.action == "get_personal_models":
            return self.model.objects.filter(owner=user)

        elif self.action == "shared_with_me":
            folder_content_type = ContentType.objects.get_for_model(self.model)
            shared_models_ids = Share.objects.filter(
                shared_with=user, content_type=folder_content_type, can_read=True
            ).values_list("object_id", flat=True)
            return self.model.objects.filter(id__in=shared_models_ids)

        elif self.action == "retrieve":
            folder_content_type = ContentType.objects.get_for_model(self.model)
            shared_models_ids = Share.objects.filter(
                shared_with=user, content_type=folder_content_type, can_read=True
            ).values_list("object_id", flat=True)
            return self.model.objects.filter(Q(owner=user) | Q(id__in=shared_models_ids))

        return super().get_queryset()

    @action(detail=False, methods=["get"], url_path="personal")
    def personal(self, request, *args, **kwargs):
        return self.get_personal_models(request, *args, **kwargs)

    @action(detail=False, methods=["get"])
    def shared_with_me(self, request, *args, **kwargs):
        return self.get_shared_with_me(request, *args, **kwargs)


class FolderViewSet(BaseViewSet):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    model = Folder


class FileViewSet(
    BaseViewSet,
    # Custom Mixinxs
    FileDownloadMixin
    ):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    model = File

    @extend_schema(
        operation_id="upload_file",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "format": "binary"},
                    "folder": {"type": "integer", "format": "int64"},
                },
            },
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=['get'])
    def download(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        return self.download_file(pk)
