from django.db import transaction
from django.contrib.auth import authenticate
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from oauth2_provider.models import get_application_model
from . import serializers as user_serializers, models as user_models, utils as user_utils

oauth2_user = user_utils.ApplicationUser()


class AuthenticationViewSet(viewsets.ViewSet):
    @action(methods=['POST'], detail=False)
    def login(self, request):
        serializer = user_serializers.LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        username = validated_data['username']
        password = validated_data['password']
        user = authenticate(username=username, password=password)

        if user is None:
            return Response({"details": "Invalid email or password"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            instance = get_application_model().objects.get(user=user)
        except get_application_model().DoesNotExist:
            return Response({"details": "Invalid client"}, status=status.HTTP_400_BAD_REQUEST)

        dt = {
            "grant_type": "password",
            "username": user.username,
            "password": password,
            "client_id": instance.client_id,
            "client_secret": instance.client_secret
        }

        response = oauth2_user.get_client_details(dt)

        if not response:
            return Response({"details": "Invalid client"}, status=status.HTTP_400_BAD_REQUEST)

        userinfo = {
            "access_token": response['access_token'],
            "expires_in": response['expires_in'],
            "token_type": response['token_type'],
            "refresh_token": response['refresh_token'],
            "jwt_token": oauth2_user.generate_jwt_token(user)
        }
        return Response({"details": userinfo}, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def register(self, request):
        serializer = user_serializers.RegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            validated_data = serializer.validated_data
            password = validated_data.pop('password')
            # create user
            instance = user_models.User.objects.create(**validated_data)
            instance.set_password(password)
            instance.save()

            oauth2_user.create_application_user(instance)
            return Response({"details": "Successfully registered"}, status=status.HTTP_200_OK)
