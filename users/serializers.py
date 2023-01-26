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
        fields = ['user_id', 'first_name', 'last_name', 'middle_name', 'username']

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

        if property_instance.owner != self.context['user']:
            raise serializers.ValidationError("You are not the owner of this property")

        attrs['property_id'] = property_instance
        return attrs


