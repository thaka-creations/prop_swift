from django.db import models
from users.models import User


# Create your models here.
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class TaskModel(BaseModel):
    title = models.CharField(max_length=1000)
    due_date = models.DateField()
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks", null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
