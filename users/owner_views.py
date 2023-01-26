from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from . import serializers as user_serializers, models as user_models, utils as user_utils

oauth2_user = user_utils.ApplicationUser()


class OwnerViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    @action(
        methods=['POST'],
        detail=False,
        url_path='add-manager'
    )
    def add_manager(self, request):
        serializer = user_serializers.AddPropertyManagerSerializer(
            data=request.data, context={'user': request.user}
        )
        if not serializer.is_valid():
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        property_instance = validated_data.pop('property_id')

        with transaction.atomic():
            password = validated_data.pop('password')
            # create user
            instance = user_models.User.objects.create(**validated_data)
            instance.set_password(password)
            instance.save()

            oauth2_user.create_application_user(instance)

            # add property manager



