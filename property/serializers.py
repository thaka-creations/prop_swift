from rest_framework import serializers
from . import models as property_models


class ListPropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = property_models.Property
        exclude = ['owners', 'tenants']


class AddPropertySerializer(serializers.Serializer):
    area_choices = [
        ("acres", "acres"),
        ("hectares", "hectares"),
        ("square feet", "square feet"),
        ("square meters", "square meters"),
    ]
    name = serializers.CharField(required=True)
    location = serializers.CharField(required=True)
    area = serializers.CharField(required=True)
    area_unit = serializers.CharField(required=True, choices=area_choices)
    rent_amount = serializers.CharField(required=True, allow_blank=True, allow_null=True)
    is_owner = serializers.BooleanField(required=True)

