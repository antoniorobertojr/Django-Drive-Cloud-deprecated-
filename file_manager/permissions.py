from rest_framework.permissions import IsAuthenticated

from .models import ContentType, File, Folder, Share


class IsOwner(IsAuthenticated):
    message = "You must be the owner of this folder or it must be shared with you to access it."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class CurrentUserCanAccess(IsAuthenticated):
    def _get_content_type(self, obj):
        if isinstance(obj, Folder):
            return ContentType.objects.get_for_model(Folder)
        elif isinstance(obj, File):
            return ContentType.objects.get_for_model(File)
        else:
            return None

    def has_object_permission(self, request, view, obj):
        content_type = self._get_content_type(obj)
        if not content_type:
            return False

        return self.check_permission(request, obj, content_type)

    def check_permission(self, request, obj, content_type):
        raise NotImplementedError("Subclasses must implement this method")


class CurrentUserCanRead(CurrentUserCanAccess):
    message = "You do not have read permissions for this object."

    def check_permission(self, request, obj, content_type):
        return Share.objects.filter(
            content_type=content_type,
            object_id=obj.id,
            shared_with=request.user,
            can_read=True
        ).exists()

class CurrentUserCanEdit(CurrentUserCanAccess):
    message = "You do not have edit permissions for this object."

    def check_permission(self, request, obj, content_type):
        return Share.objects.filter(
            content_type=content_type,
            object_id=obj.id,
            shared_with=request.user,
            can_edit=True
        ).exists()

class CurrentUserCanShare(CurrentUserCanAccess):
    message = "You do not have share permissions for this object."

    def check_permission(self, request, obj, content_type):
        return Share.objects.filter(
            content_type=content_type,
            object_id=obj.id,
            shared_with=request.user,
            can_share=True
        ).exists()

class CurrentUserCanDelete(CurrentUserCanAccess):
    message = "You do not have delete permissions for this object."

    def check_permission(self, request, obj, content_type):
        return Share.objects.filter(
            content_type=content_type,
            object_id=obj.id,
            shared_with=request.user,
            can_delete=True
        ).exists()
