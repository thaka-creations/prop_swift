from rest_framework import serializers
from . models import User
from property.models import Property


class RegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    middle_name = serializers.CharField(required=True, allow_blank=True, allow_null=True)
    username = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({'username': 'Email already exists'})

        if attrs.get("password") != attrs.pop("confirm_password"):
            raise serializers.ValidationError("Passwords don't match")
        return attrs


class LoginSerializer(serializers.Serializer):
    username = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)


class UserProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['user_id', 'first_name', 'last_name', 'middle_name', 'username', 'is_manager']

    @staticmethod
    def get_user_id(obj):
        return obj.id


class AddPropertyManagerSerializer(RegistrationSerializer):
    property_id = serializers.UUIDField(required=True)

    def validate(self, attrs):
        super().validate(attrs)

        try:
            property_instance = Property.objects.get(id=attrs['property_id'])
        except Property.DoesNotExist:
            raise serializers.ValidationError("Property does not exist")

        if not property_instance.owners.filter(id=self.context['user'].id).exists():
            raise serializers.ValidationError("You are not the owner of this property")

        attrs['property_id'] = property_instance
        return attrs


class RemovePropertyManagerSerializer(serializers.Serializer):
    property_id = serializers.UUIDField(required=True)
    manager = serializers.UUIDField(required=True)

    def validate(self, attrs):
        try:
            property_instance = Property.objects.get(id=attrs['property_id'])
        except Property.DoesNotExist:
            raise serializers.ValidationError("Property does not exist")

        if not property_instance.owners.filter(id=self.context['user'].id).exists():
            raise serializers.ValidationError("You are not the owner of this property")

        try:
            manager_instance = User.objects.get(id=attrs['manager'])
        except User.DoesNotExist:
            raise serializers.ValidationError("Manager does not exist")

        if not property_instance.managers.filter(id=manager_instance.id).exists():
            raise serializers.ValidationError("Manager is not assigned to this property")

        attrs['property_id'] = property_instance
        attrs['manager'] = manager_instance
        return attrs






