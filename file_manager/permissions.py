from rest_framework.permissions import IsAuthenticated

from .models import ContentType, File, Folder, Share


class IsOwner(IsAuthenticated):
    message = "You must be the owner of this object or it must be shared with you to access it."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class CanAccess(IsAuthenticated):
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


class CanRead(CanAccess):
    message = "You do not have read permissions for this object."

    def check_permission(self, request, obj, content_type):
        return Share.objects.filter(
            content_type=content_type,
            object_id=obj.id,
            shared_with=request.user,
            can_read=True,
        ).exists()


class CanEdit(CanAccess):
    message = "You do not have edit permissions for this object."

    def check_permission(self, request, obj, content_type):
        return Share.objects.filter(
            content_type=content_type,
            object_id=obj.id,
            shared_with=request.user,
            can_edit=True,
        ).exists()


class CanShare(CanAccess):
    message = "You do not have share permissions for this object."

    def check_permission(self, request, obj, content_type):
        return Share.objects.filter(
            content_type=content_type,
            object_id=obj.id,
            shared_with=request.user,
            can_share=True,
        ).exists()


class CanDelete(CanAccess):
    message = "You do not have delete permissions for this object."

    def check_permission(self, request, obj, content_type):
        return Share.objects.filter(
            content_type=content_type,
            object_id=obj.id,
            shared_with=request.user,
            can_delete=True,
        ).exists()


class CanEditParentFolder(IsAuthenticated):
    message = "You do not have permission to create a folder in this location."

    def has_object_permission(self, request, view):
        # If it's not a 'create' action, this check is not needed
        if view.action != "create":
            return True

        parent_id = request.data.get("parent")

        # If no parent_id, it's a root folder, allow creation
        if not parent_id:
            return True

        try:
            parent_folder = Folder.objects.get(pk=parent_id)
        except Folder.DoesNotExist:
            # If parent folder does not exist, deny permission
            return False

        # If the user is the owner of the parent folder, allow creation
        if parent_folder.owner == request.user:
            return True

        # Check if the user has edit permissions on the parent folder
        folder_content_type = ContentType.objects.get_for_model(Folder)
        return Share.objects.filter(
            shared_with=request.user,
            content_type=folder_content_type,
            object_id=parent_id,
            can_edit=True,
        ).exists()
