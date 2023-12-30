from rest_framework.permissions import BasePermission


class IsOwnerOrSharedWith(BasePermission):
    message = "You must be the owner of this folder or it must be shared with you to access it."

    def has_object_permission(self, request, view, obj):
        if obj.user == request.user:
            return True

        return request.user in obj.shared_with.all()


class IsOwner(BasePermission):
    message = "You must be the owner to perform this action on this object."

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

