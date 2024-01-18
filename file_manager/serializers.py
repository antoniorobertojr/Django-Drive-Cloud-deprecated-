from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import File, Folder

User = get_user_model()


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ["id", "name", "file", "created_at", "updated_at"]


class FolderSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()
    owner = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Folder
        fields = ["id", "name", "owner", "parent", "children", "files"]

    def get_children(self, obj):
        children = obj.children.values("id", "name")
        return list(children)

    def get_files(self, obj):
        files = obj.file_set.all()
        return FileSerializer(files, many=True).data


class ShareSerializer(serializers.Serializer):
    usernames = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=True
    )
    can_read = serializers.BooleanField(default=True)
    can_edit = serializers.BooleanField(default=False)
    can_delete = serializers.BooleanField(default=False)
    can_share = serializers.BooleanField(default=False)

    def validate_usernames(self, value):
        # Ensure all provided usernames exist
        valid_usernames = []
        for username in value:
            if not User.objects.filter(username=username).exists():
                raise serializers.ValidationError(f"User with username {username} does not exist.")
            valid_usernames.append(username)
        return valid_usernames
