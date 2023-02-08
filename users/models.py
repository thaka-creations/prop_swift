import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .manager import UserManager


# Create your models here.
ACCOUNT_STATUS = [
    ("ACTIVE", "ACTIVE"),
    ("DEACTIVATED", "DEACTIVATED"),
    ("SUSPENDED", "SUSPENDED"),
]


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, null=True, blank=True)
    account_status = models.CharField(max_length=255, choices=ACCOUNT_STATUS, default='ACTIVE')
    is_manager = models.BooleanField(default=False)

    USERNAME_FIELD = "username"

    objects = UserManager()

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    class Meta:
        ordering = ["-created_at"]

