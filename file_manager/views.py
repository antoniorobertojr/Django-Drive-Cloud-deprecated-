from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response

from .models import Folder
from .permissions import IsOwner, IsOwnerOrSharedWith
from .serializers import FolderSerializer

User = get_user_model()


from rest_framework.decorators import action
from rest_framework.response import Response


class FolderViewSet(viewsets.ModelViewSet):
    queryset = Folder.objects.all()
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

    @action(detail=True, methods=['post'], permission_classes=[IsOwner])
    def share(self, request, pk=None):
        folder = get_object_or_404(Folder, id=pk)

        # Manually check object permissions
        self.check_object_permissions(request, folder)

        user_to_share_with = User.objects.get(username=request.data.get("username"))
        folder.shared_with.add(user_to_share_with)
        return Response({"status": "folder shared"}, status=status.HTTP_200_OK)


    @action(detail=True, methods=['post'], permission_classes=[IsOwner])
    def unshare(self, request, pk=None):
        folder = get_object_or_404(Folder, id=pk)
        self.check_object_permissions(request, folder)

        user_to_unshare_with = User.objects.get(username=request.data.get("username"))
        folder.shared_with.remove(user_to_unshare_with)
        return Response({"status": "folder unshared"}, status=status.HTTP_200_OK)

# Common
# class SearchView(generics.GenericAPIView):
#     def get(self, request, *args, **kwargs):
#         query = request.query_params.get("q", "")

#         # Search in Files
#         files = File.objects.filter(name__icontains=query)
#         file_serializer = FileSerializer(files, many=True)

#         # Search in Folders
#         folders = Folder.objects.filter(name__icontains=query)
#         folder_serializer = FolderSerializer(folders, many=True)

#         return Response(
#             {"files": file_serializer.data, "folders": folder_serializer.data},
#             status=status.HTTP_200_OK,
#         )
