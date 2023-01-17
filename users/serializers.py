from rest_framework import serializers
from . models import User


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
