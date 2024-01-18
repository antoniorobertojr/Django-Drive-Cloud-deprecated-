from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from file_manager.models import Share
from file_manager.permissions import CurrentUserCanShare, IsOwner
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

User = get_user_model()


class ShareModelMixin:
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsOwner | CurrentUserCanShare],
    )
    def share(self, request, pk=None):
        obj = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            return self._process_sharing(request, obj, serializer.validated_data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _process_sharing(self, request, obj, validated_data):
        current_user = request.user
        usernames = validated_data["usernames"]
        permissions = {
            "can_read": validated_data["can_read"],
            "can_edit": validated_data["can_edit"],
            "can_delete": validated_data["can_delete"],
            "can_share": validated_data["can_share"],
        }

        if request.user.username in usernames:
            return Response(
                {"error": "Cannot share with yourself"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        successful_shares, failed_shares = self._share_with_users(
            obj, current_user, usernames, permissions
        )

        return Response(
            {
                "status": "Sharing process completed",
                "shared_with": successful_shares,
                "failed_to_share_with": failed_shares,
            },
            status=status.HTTP_200_OK,
        )

    def _share_with_users(self, obj, shared_by, usernames, permissions):
        successful_shares = []
        failed_shares = []
        content_type = ContentType.objects.get_for_model(obj)

        for username in usernames:
            try:
                user_to_share_with = User.objects.get(username=username)
                Share.objects.update_or_create(
                    shared_by=shared_by,
                    shared_with=user_to_share_with,
                    content_type=content_type,
                    object_id=obj.id,
                    defaults=permissions,
                )
                successful_shares.append(username)
            except User.DoesNotExist:
                failed_shares.append(username)

        return successful_shares, failed_shares


class UnshareModelMixin:
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsOwner | CurrentUserCanShare],
    )
    def unshare(self, request, pk=None):
        obj = self.get_object()
        username = request.data.get("username")
        user_to_unshare_with = get_object_or_404(User, username=username)

        if obj.owner == user_to_unshare_with:
            return Response(
                {"error": "Cannot unshare with the owner"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        content_type = ContentType.objects.get_for_model(obj)

        Share.objects.filter(
            shared_with=user_to_unshare_with,
            content_type=content_type,
            object_id=obj.id,
        ).delete()

        return Response(
            {"status": f"{obj} unshared from {username}"}, status=status.HTTP_200_OK
        )


class SharedWithMeMixin:
    @action(detail=False, methods=["get"])
    def shared_with_me(self, request, *args, **kwargs):
        model = self.queryset.model
        model_content_type = ContentType.objects.get_for_model(model)
        shared_objects_ids = Share.objects.filter(
            shared_with=request.user, content_type=model_content_type, can_read=True
        ).values_list("object_id", flat=True)

        shared_objects = model.objects.filter(id__in=shared_objects_ids)
        serializer = self.get_serializer(shared_objects, many=True)
        return Response(serializer.data)


class PersonalMixin:
    @action(detail=False, methods=["get"], url_path="personal")
    def personal_folders(self, request, *args, **kwargs):
        model = self.queryset.model
        personal_folders = model.objects.filter(owner=request.user)
        serializer = self.get_serializer(personal_folders, many=True)
        return Response(serializer.data)
