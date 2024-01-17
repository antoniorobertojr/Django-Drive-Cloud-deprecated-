from rest_framework.permissions import IsAuthenticated

from .models import ContentType, File, Folder, Share


class IsOwner(IsAuthenticated):
    message = "You must be the owner of this folder or it must be shared with you to access it."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class CurrentUserCanRead(IsAuthenticated):
    message = "Access to this item is restricted."

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Folder):
            content_type = ContentType.objects.get_for_model(Folder)
        elif isinstance(obj, File):
            content_type = ContentType.objects.get_for_model(File)
        else:
            return False

        shared_access = Share.objects.filter(
            content_type=content_type,
            object_id=obj.id,
            shared_with=request.user,
            can_read=True  # Assuming we are checking for read permission
        ).exists()

        # Grant permission if the object is shared with the current user with read access
        return shared_access
