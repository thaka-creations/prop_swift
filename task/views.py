from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from shared_utils import error_utils
from . import models as task_models, serializers as task_serializers


class TaskViewSet(viewsets.ViewSet):
    queryset = task_models.TaskModel.objects.all()
    serializer_class = task_serializers.TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset

    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(*args, **kwargs)

    def get_object(self):
        try:
            return self.get_queryset().get(id=self.request.data.get("request_id"))
        except task_models.TaskModel.DoesNotExist:
            return None

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(actor=self.request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response({"details": serializer.data}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({"details": error_utils.format_error(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            serializer.save(
                actor=request.user
            )
        return Response({"details": "Task created successfully"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["POST"], url_path="remove-task")
    def remove_task(self, request, *args, **kwargs):
        if not self.request.data.get("request_id"):
            return Response({"details": "Request id is required"}, status=status.HTTP_400_BAD_REQUEST)
        task = self.get_object()
        if not task:
            return Response({"details": "Task does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        task.delete()
        return Response({"details": "Task deleted successfully"}, status=status.HTTP_200_OK)


