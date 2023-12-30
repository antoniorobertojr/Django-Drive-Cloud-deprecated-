from django.shortcuts import get_object_or_404
from rest_framework import generics, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Folder
from .permissions import IsOwner, IsOwnerOrSharedWith
from .serializers import FolderSerializer


class FolderCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer


class FolderReadOneView(generics.RetrieveAPIView):
    queryset = Folder.objects.all()
    permission_classes = [IsOwnerOrSharedWith]
    serializer_class = FolderSerializer


class FolderViewSet(viewsets.ModelViewSet):
    serializer_class = FolderSerializer
    permission_classes = [IsOwnerOrSharedWith]

    def get_queryset(self):
        queryset = Folder.objects.all()
        name = self.request.query_params.get("name", None)
        parent_id = self.request.query_params.get("parent", None)

        if name:
            queryset = queryset.filter(name__icontains=name)

        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)

        return queryset


class FolderDeleteView(generics.DestroyAPIView):
    permission_classes = [IsOwner]
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
