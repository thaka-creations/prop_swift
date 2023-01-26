from rest_framework import serializers
from . import models as task_models


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = task_models.TaskModel
        fields = "__all__"
        extra_kwargs = {
            "id": {"read_only": True},
            }
