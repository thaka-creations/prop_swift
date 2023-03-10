from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from shared_utils import error_utils
from . import serializers as user_serializers, models as user_models, utils as user_utils
from property import models as property_models

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
            return Response({"details": error_utils.format_error(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        property_instance = validated_data.pop('property_id')

        with transaction.atomic():
            password = validated_data.pop('password')
            # create user
            instance = user_models.User.objects.create(**validated_data, is_manager=True)
            instance.set_password(password)
            instance.save()

            oauth2_user.create_application_user(instance)

            # add property manager
            property_instance.managers.add(instance)
            return Response({"details": "Successfully added manager"}, status=status.HTTP_200_OK)

    @action(
        methods=['POST'],
        detail=False,
        url_path='remove-manager'
    )
    def remove_manager(self, request):
        serializer = user_serializers.RemovePropertyManagerSerializer(
            data=request.data, context={'user': request.user}
        )

        if not serializer.is_valid():
            return Response({"details": error_utils.format_error(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        property_instance = validated_data.pop('property_id')
        manager_instance = validated_data.pop('manager')

        with transaction.atomic():
            property_instance.managers.remove(manager_instance)
            manager_instance.delete()
            return Response({"details": "Successfully removed manager"}, status=status.HTTP_200_OK)

    @action(
        methods=['GET'],
        detail=False,
        url_path='list-managers'
    )
    def list_managers(self, request):
        property_id = request.query_params.get('property_id')
        if not property_id:
            return Response({"details": "Property id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            instance = property_models.Property.objects.get(id=property_id)
        except property_models.Property.DoesNotExist:
            return Response({"details": "Property does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        if not instance.owners.filter(id=request.user.id).exists():
            return Response({"details": "You are not the owner of this property"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = user_serializers.UserProfileSerializer(instance.managers.all(), many=True)
        return Response({"details": serializer.data}, status=status.HTTP_200_OK)




