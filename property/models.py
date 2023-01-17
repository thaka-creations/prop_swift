import uuid
import os
from datetime import datetime
from django.db import models
from users.models import User


# Create your models here.
def file_upload(instance, filename):
    ext = filename.split(".")[-1]
    now = datetime.now()

    if len(str(abs(now.month))) > 1:
        month = str(now.month)
    else:
        month = str(now.month).zfill(2)

    if len(str(abs(now.day))) > 1:
        day = str(now.day)
    else:
        day = str(now.day).zfill(2)

    if len(str(abs(now.hour))) > 1:
        hour = str(now.hour)
    else:
        hour = str(now.hour).zfill(2)

    upload_to = f"{str(now.year)}/{month}/{day}/{hour}"
    if instance.pk:
        filename = "{}.{}".format(instance.pk, ext)
    else:
        filename = "{}.{}".format(uuid.uuid4().hex, ext)
    return os.path.join(upload_to, filename)


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class Property(BaseModel):
    area_choices = [
        ("acres", "acres"),
        ("hectares", "hectares"),
        ("square feet", "square feet"),
        ("square meters", "square meters"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=1000)
    location = models.CharField(max_length=1000)
    area = models.FloatField(blank=True, null=True)
    area_unit = models.CharField(max_length=255, choices=area_choices, blank=True, null=True)
    rent_amount = models.DecimalField(max_digits=13, decimal_places=2, blank=True, null=True)
    owners = models.ManyToManyField(User, related_name="property_owners")
    tenants = models.ManyToManyField(User, related_name="property_tenants")


class PropertyImages(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="property_images")
    image = models.FileField(upload_to=file_upload, blank=True, null=True)


class PropertyRent(BaseModel):
    rent_status_choices = [
        ("paid", "paid"),
        ("unpaid", "unpaid"),
        ("overdue", "overdue"),
        ("partially_paid", "partially_paid"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="property_rent")
    amount = models.DecimalField(max_digits=13, decimal_places=2, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    rent_status = models.CharField(max_length=255, choices=rent_status_choices, blank=True, null=True)


class PropertyExpense(BaseModel):
    expense_type_choices = [
        ("general", "general"),
        ("incurred", "incurred"),
        ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="property_expenses")
    expense_type = models.CharField(max_length=255, choices=expense_type_choices, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=13, decimal_places=2, blank=True, null=True)
    date_incurred = models.DateField(blank=True, null=True)
