from rest_framework import viewsets
from . import models as task_models, serializers as task_serializers


class TaskViewSet(viewsets.ModelViewSet):
    queryset = task_models.TaskModel.objects.all()
    serializer_class = task_serializers.TaskSerializer
