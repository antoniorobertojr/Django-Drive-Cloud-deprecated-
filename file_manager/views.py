from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, viewsets
from rest_framework.decorators import action

from file_manager.mixins.views import (
    CustomCreateModelMixin,
    FileDownloadMixin,
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
from .serializers import (
    FileSerializer,
    FolderSerializer,
    ShareSerializer,
    UnshareSerializer,
)


class BaseViewSet(
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    CustomCreateModelMixin,
    ShareModelMixin,
    UnshareModelMixin,
    SharedWithMeMixin,
    PersonalMixin,
):
    model = None
    action_to_permission = {
        "retrieve": [IsOwner | CanRead],
        "download": [IsOwner | CanRead],
        "personal": [IsOwner | CanRead],
        "shared_with_me": [IsOwner | CanRead],
        "update": [IsOwner | CanEdit],
        "partial_update": [IsOwner | CanEdit],
        "share": [IsOwner | CanShare],
        "unshare": [IsOwner | CanShare],
        "destroy": [IsOwner | CanDelete],
        "create": [CanEditParentFolder],
    }

    def get_serializer_class(self):
        if self.action == "share":
            return ShareSerializer
        elif self.action == "unshare":
            return UnshareSerializer
        return self.serializer_class

    def get_permissions(self):
        permission_classes = self.action_to_permission.get(
            self.action, [CanEditParentFolder]
        )
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        if self.action in ["personal", "get_personal_models"]:
            return self.model.objects.filter(owner=self.request.user)
        if self.action == "shared_with_me":
            content_type = ContentType.objects.get_for_model(self.model)
            shared_ids = Share.objects.filter(
                shared_with=self.request.user, content_type=content_type, can_read=True
            ).values_list("object_id", flat=True)
            return self.model.objects.filter(id__in=shared_ids)
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


class FileViewSet(BaseViewSet, FileDownloadMixin):
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
            }
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=["get"])
    def download(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        return self.download_file(pk)
