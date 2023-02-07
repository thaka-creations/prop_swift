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


class ListMyPropertiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = property_models.Property
        fields = ['id', 'name']


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


class ListPropertyExpenseSerializer(serializers.ModelSerializer):
    property = ListPropertySerializer(read_only=True)
    files = serializers.SerializerMethodField()

    class Meta:
        model = property_models.PropertyExpense
        fields = '__all__'

    @staticmethod
    def get_files(obj):
        host = os.environ.get('CALLBACK_SERVICE', None)
        return [host + settings.MEDIA_URL + str(f.file) for f in obj.expense_images.all()]


class ListOtherReceiptsSerializer(serializers.ModelSerializer):
    files = serializers.SerializerMethodField()

    class Meta:
        model = property_models.OtherReceipts
        fields = '__all__'

    @staticmethod
    def get_files(obj):
        host = os.environ.get('CALLBACK_SERVICE', None)
        return [host + settings.MEDIA_URL + str(f.file) for f in obj.other_receipt_images.all()]


class CreatePropertyExpenseSerializer(serializers.ModelSerializer):
    property_id = serializers.UUIDField(write_only=True, required=True)
    receipt = serializers.CharField(required=False)
    files = serializers.ListField(required=True, child=serializers.UUIDField(),
                                  allow_null=True, allow_empty=True)

    class Meta:
        model = property_models.PropertyExpense
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'property': {'read_only': True},
        }

    def validate(self, attrs):
        qs = property_models.PropertyImages.objects.filter(id__in=attrs['files'])
        if qs.count() != len(attrs['files']):
            raise serializers.ValidationError("File(s) attached not found")
        attrs['files'] = qs
        return attrs


class CreateOtherReceiptsSerializer(serializers.ModelSerializer):
    property_id = serializers.UUIDField(write_only=True, required=True)
    receipt = serializers.CharField(required=True)
    files = serializers.ListField(required=True, child=serializers.UUIDField(),
                                  allow_null=True, allow_empty=True)

    class Meta:
        model = property_models.OtherReceipts
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'property': {'read_only': True},
        }

    def validate(self, attrs):
        qs = property_models.PropertyImages.objects.filter(id__in=attrs['files'])
        if qs.count() != len(attrs['files']):
            raise serializers.ValidationError("File(s) attached not found")
        attrs['files'] = qs
        return attrs


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
        if not attrs['is_owner']:
            if not attrs['rent_amount']:
                raise serializers.ValidationError("Rent amount is required")

        qs = property_models.PropertyImages.objects.filter(id__in=attrs['files'])
        if qs.count() != len(attrs['files']):
            raise serializers.ValidationError("File(s) attached not found")
        attrs['files'] = qs
        return attrs


class AddRentPaymentSerializer(serializers.Serializer):
    request_id = serializers.UUIDField(required=True)
    amount = serializers.DecimalField(max_digits=13, decimal_places=2, required=True)
    receipt = serializers.CharField(required=True)
    files = serializers.ListField(required=True, child=serializers.UUIDField(),
                                    allow_null=True, allow_empty=True)

    def validate(self, attrs):
        amount = attrs['amount']
        try:
            instance = property_models.PropertyRent.objects.get(id=attrs['request_id'])
        except property_models.PropertyRent.DoesNotExist:
            raise serializers.ValidationError("Rent request does not exist")

        if instance.rent_status == 'paid':
            raise serializers.ValidationError("Rent is already paid")

        if instance.amount < amount:
            raise serializers.ValidationError("Amount paid cannot be more than amount due")

        elif instance.amount > amount:
            raise serializers.ValidationError("Amount paid is less than amount due")

        qs = property_models.PropertyImages.objects.filter(id__in=attrs['files'])
        if qs.count() != len(attrs['files']):
            raise serializers.ValidationError("File(s) attached not found")

        attrs['instance'] = instance
        attrs['files'] = qs
        return attrs


