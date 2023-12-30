from rest_framework import serializers

from .models import Folder


class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = FolderSerializer(value, context=self.context)
        return serializer.data

class FolderSerializer(serializers.ModelSerializer):
    children = serializers.ListSerializer(child=RecursiveField(), required=False)

    class Meta:
        model = Folder
        fields = ['id', 'name', 'parent', 'children']
