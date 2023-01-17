from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from . import serializers as user_serializers, models as user_models


class AuthenticationViewSet(viewsets.ViewSet):
    @action(methods=['POST'], detail=False)
    def login(self, request):
        pass

    @action(methods=['POST'], detail=False)
    def register(self, request):
        serializer = user_serializers.RegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # create user
            password = serializer.validated_data.pop('password')
            instance = user_models.User.objects.create(**serializer.validated_data)
            instance.set_password(password)
            instance.save()

            return Response({"details": "User created successfully"}, status=status.HTTP_201_CREATED)


