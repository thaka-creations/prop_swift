from django.db import transaction
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from . import models as property_models, serializers as property_serializers


class PropertyViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    @action(
        methods=['POST'],
        detail=False,
        url_path='upload-file',
    )
    def upload_file(self, request):
        documents = []
        with transaction.atomic():
            for k, v in request.data.items():
                for f in request.FILES.getlist(str(k)):
                    try:
                        instance = property_models.PropertyImages.objects.create(
                            file=f,
                            uploader=request.user
                        )
                    except PermissionError:
                        return Response(
                            {"details": "Could not upload file"},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    documents.append(str(instance.id))

            if not documents:
                return Response(
                    {"details": "No files uploaded"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response({"details": documents}, status=status.HTTP_200_OK)

    @action(
        methods=['POST'],
        detail=False,
        url_path='add-property'
    )
    def add_property(self, request):
        serializer = property_serializers.AddPropertySerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        is_owner = validated_data.pop('is_owner')
        files = validated_data.pop('files')

        with transaction.atomic():
            instance = property_models.Property.objects.create(**validated_data)
            if is_owner:
                instance.owners.add(request.user)
            else:
                instance.tenants.add(request.user)

            if files.exists():
                files.update(property=instance)
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

    @action(
        methods=['GET'],
        detail=False,
        url_path='list-rentals'
    )
    def list_rentals(self, request):
        # with date filters and property filters
        # paid, unpaid, overdue
        property_id = request.query_params.get('property_id', None)
        filter_type = request.query_params.get('filter', None)

        filter_params = {
            Q(property__owners=request.user) | Q(property__tenants=request.user)
        }

        if property_id:
            filter_params.update({'property__id': property_id})

        if filter_type:
            filter_params.update({'rent_status': filter_type})

        qs = property_models.PropertyRent.objects.filter(
            *filter_params)

    @action(
        methods=['GET'],
        detail=False,
        url_path='list-expenses'
    )
    def list_expenses(self, request):
        # with date filters and property filters
        # general, specific
        pass
