from datetime import datetime
from rest_framework import serializers
from . import models as task_models


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = task_models.TaskModel
        fields = "__all__"
        extra_kwargs = {
            "id": {"read_only": True},
            }

    def validate(self, attrs):
        if attrs["due_date"] < datetime.now().date():
            raise serializers.ValidationError("Due date cannot be less than today")
        return attrs
