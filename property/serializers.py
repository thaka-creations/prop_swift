import os
from django.conf import settings
from rest_framework import serializers
from . import models as property_models


class ListPropertySerializer(serializers.ModelSerializer):
    files = serializers.SerializerMethodField()

    class Meta:
        model = property_models.Property
        exclude = ['owners', 'tenants']

    @staticmethod
    def get_files(obj):
        host = os.environ.get('CALLBACK_SERVICE', None)
        return [host + settings.MEDIA_URL + str(f.file) for f in obj.property_images.all()]


class ListPropertyRentSerializer(serializers.ModelSerializer):
    property = ListPropertySerializer()

    class Meta:
        model = property_models.PropertyRent
        fields = [
            'id',
            'amount',
            'amount_paid',
            'start_date',
            'due_date',
            'date_paid',
            'rent_status',
            'property'
        ]


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
    area_unit = serializers.ChoiceField(choices=area_choices, required=True)
    rent_amount = serializers.DecimalField(max_digits=13, decimal_places=2, required=True, allow_null=True)
    is_owner = serializers.BooleanField(required=True)
    files = serializers.ListField(required=True, child=serializers.UUIDField(),
                                  allow_null=True, allow_empty=True)

    def validate(self, attrs):
        qs = property_models.PropertyImages.objects.filter(id__in=attrs['files'])
        if qs.count() != len(attrs['files']):
            raise serializers.ValidationError("File(s) attached not found")
        attrs['files'] = qs
        return attrs


