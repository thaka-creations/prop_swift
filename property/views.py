from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from . import models as property_models, serializers as property_serializers


class PropertyViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    @action(
        methods=['GET'],
        detail=False,
        url_path='add-property'
    )
    def add_property(self, request):
        serializer = property_serializers.AddPropertySerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        is_owner = validated_data.pop('is_owner')
        if is_owner:
            validated_data['owners'] = request.user
        else:
            validated_data['tenants'] = request.user

        with transaction.atomic():
            property_models.Property.objects.create(**validated_data)
            return Response({"details": "Property added successfully"}, status=status.HTTP_200_OK)

    @action(
        methods=['GET'],
        detail=False,
        url_path='list-owned-properties'
    )
    def list_owned_properties(self, request):
        qs = property_models.Property.objects.filter(owners=request.user)
        serializer = property_serializers.ListPropertySerializer(qs, many=True)
        return Response({"details": serializer.data}, status=status.HTTP_200_OK)

    @action(
        methods=['GET'],
        detail=False,
        url_path='list-rented-properties'
    )
    def list_rented_properties(self, request):
        qs = property_models.Property.objects.filter(tenants=request.user)
        serializer = property_serializers.ListPropertySerializer(qs, many=True)
        return Response({"details": serializer.data}, status=status.HTTP_200_OK)

    def list_rentals(self, request):
        # with date filters and property filters
        # paid, unpaid, overdue
        pass

    def list_expenses(self, request):
        # with date filters and property filters
        # general, specific
        pass
