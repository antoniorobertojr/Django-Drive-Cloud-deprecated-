from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.fields import FileField

from .models import File, Folder

User = get_user_model()


class FileSerializer(serializers.ModelSerializer):
    file = serializers.FileField()
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = File
        fields = ["id", "file", "owner", "folder", "created_at", "updated_at"]


class FolderSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Folder
        fields = ["id", "name", "owner", "parent", "children", "files"]

    def get_children(self, obj):
        print("Type of obj in get_children:", type(obj))
        children = obj.children.values("id", "name") if hasattr(obj, "children") else []
        return list(children)

    def get_files(self, obj):
        print("Type of obj in get_files:", type(obj))  # For debugging
        if isinstance(obj, Folder):
            files = obj.file_set.all()
            return FileSerializer(files, many=True).data
        return []


class BaseShareSerializer(serializers.Serializer):
    usernames = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=True
    )

    def validate_usernames(self, value):
        valid_usernames = []
        for username in value:
            if not User.objects.filter(username=username).exists():
                raise serializers.ValidationError(
                    f"User with username {username} does not exist."
                )
            valid_usernames.append(username)
        return valid_usernames


class ShareSerializer(BaseShareSerializer):
    can_read = serializers.BooleanField(default=True)
    can_edit = serializers.BooleanField(default=False)
    can_delete = serializers.BooleanField(default=False)
    can_share = serializers.BooleanField(default=False)


class UnshareSerializer(BaseShareSerializer):
    pass
