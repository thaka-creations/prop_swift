from django.db import transaction
from django.db.models import Q, Sum
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from shared_utils import error_utils
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
            return Response({"details": error_utils.format_error(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        is_owner = validated_data.pop('is_owner')
        files = validated_data.pop('files')

        with transaction.atomic():
            instance = property_models.Property.objects.create(**validated_data)
            if is_owner:
                instance.owners.add(request.user)
            else:
                instance.tenants.add(request.user)

                # add first property rent
                start_date = timezone.now().replace(day=1)
                due_date = start_date + timezone.timedelta(days=30)

                property_models.PropertyRent.objects.create(
                    property=instance,
                    amount=instance.rent_amount,
                    rent_status="unpaid",
                    start_date=start_date,
                    due_date=due_date
                )

            if files.exists():
                files.update(property=instance)
            return Response({"details": "Property added successfully"}, status=status.HTTP_200_OK)

    @action(
        methods=['POST'],
        detail=False,
        url_path='remove-property'
    )
    def remove_property(self, request):
        request_id = self.request.data.get('request_id')
        if not request_id:
            return Response({"details": "Request id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            instance = property_models.Property.objects.get(id=request_id)
        except property_models.Property.DoesNotExist:
            return Response({"details": "Property does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        # check if owner or tenant
        if not instance.owners.filter(id=request.user.id).exists() and \
                not instance.tenants.filter(id=request.user.id).exists() \
                and not instance.manager.filter(id=request.user.id).exists():
            return Response({"details": "You are not an owner, tenant or manager of this property"},
                            status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            instance.delete()
            return Response({"details": "Property removed successfully"}, status=status.HTTP_200_OK)

    @action(
        methods=['POST'],
        detail=False,
        url_path='add-rent-payment'
    )
    def add_rent_payment(self, request):
        serializer = property_serializers.AddRentPaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"details": error_utils.format_error(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        instance = validated_data['instance']
        amount = validated_data['amount']
        receipt = validated_data['receipt']
        files = validated_data['files']
        payment_date = validated_data['payment_date']

        property_instance = instance.property

        if not property_instance.owners.filter(id=request.user.id).exists() and \
                not property_instance.tenants.filter(id=request.user.id).exists()\
                and not property_instance.manager.filter(id=request.user.id).exists():
            return Response({"details": "You are not an owner, tenant or manager of this property"},
                            status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            instance.amount_paid = amount
            instance.receipt = receipt
            instance.date_paid = payment_date
            instance.rent_status = "paid"
            instance.save()

            if files.exists():
                files.update(rent=instance)
            return Response({"details": "Rent paid successfully"}, status=status.HTTP_200_OK)

    @action(
        methods=['POST'],
        detail=False,
        url_path='add-expense'
    )
    def add_expense(self, request):
        serializer = property_serializers.CreatePropertyExpenseSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"details": error_utils.format_error(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        property_id = validated_data.pop('property_id')
        files = validated_data.pop('files')

        try:
            instance = property_models.Property.objects.get(id=property_id)
        except property_models.Property.DoesNotExist:
            return Response({"details": "Property does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        if not instance.owners.filter(id=request.user.id).exists() and \
                not instance.tenants.filter(id=request.user.id).exists() and \
                not instance.manager.filter(id=request.user.id).exists():
            return Response({"details": "You are not an owner, tenant or manager of this property"},
                            status=status.HTTP_400_BAD_REQUEST)

        validated_data['property'] = instance

        with transaction.atomic():
            expense_instance = serializer.save(**validated_data)
            if files.exists():
                files.update(expense=expense_instance)
            return Response({"details": "Expense added successfully"}, status=status.HTTP_200_OK)

    @action(
        methods=['POST'],
        detail=False,
        url_path='delete-expense'
    )
    def delete_expense(self, request):
        request_id = self.request.data.get('request_id')
        if not request_id:
            return Response({"details": "Request id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            instance = property_models.PropertyExpense.objects.get(id=request_id)
        except property_models.PropertyExpense.DoesNotExist:
            return Response({"details": "Expense does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        property_instance = instance.property

        if not property_instance.owners.filter(id=request.user.id).exists() and \
                not property_instance.tenants.filter(id=request.user.id).exists() and \
                not property_instance.manager.filter(id=request.user.id).exists():
            return Response({"details": "You are not an owner, tenant or manager of this property"},
                            status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            instance.delete()
            return Response({"details": "Expense deleted successfully"}, status=status.HTTP_200_OK)

    @action(
        methods=['POST'],
        detail=False,
        url_path='delete-other-receipt'
    )
    def delete_other_receipt(self, request):
        request_id = self.request.data.get('request_id')
        if not request_id:
            return Response({"details": "Request id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            instance = property_models.OtherReceipts.objects.get(id=request_id)
        except property_models.OtherReceipts.DoesNotExist:
            return Response({"details": "Other receipt does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        property_instance = instance.property

        if not property_instance.owners.filter(id=request.user.id).exists() and \
                not property_instance.tenants.filter(id=request.user.id).exists() and \
                not property_instance.managers.filter(id=request.user.id).exists():
            return Response({"details": "You are not an owner, tenant or manager of this property"},
                            status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            instance.delete()
            return Response({"details": "Other receipt deleted successfully"}, status=status.HTTP_200_OK)

    @action(
        methods=['POST'],
        detail=False,
        url_path='add-other-receipt'
    )
    def add_other_receipt(self, request):
        serializer = property_serializers.CreateOtherReceiptsSerializer(
            data=request.data
        )

        if not serializer.is_valid():
            return Response({"details": error_utils.format_error(serializer.errors)},
                            status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        property_id = validated_data.pop('property_id')
        files = validated_data.pop('files')

        try:
            instance = property_models.Property.objects.get(id=property_id)
        except property_models.Property.DoesNotExist:
            return Response({"details": "Property does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        if not instance.owners.filter(id=request.user.id).exists() and \
                not instance.tenants.filter(id=request.user.id).exists() \
                and not instance.managers.filter(id=request.user.id).exists():
            return Response({"details": "You are not an owner, tenant or manager of this property"},
                            status=status.HTTP_400_BAD_REQUEST)

        validated_data['property'] = instance

        with transaction.atomic():
            expense_instance = serializer.save(**validated_data)
            if files.exists():
                files.update(other_receipt=expense_instance)
            return Response({"details": "Other receipt expenses added successfully"}, status=status.HTTP_200_OK)

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
        url_path='list-my-properties'
    )
    def list_my_properties(self, request):
        qs = property_models.Property.objects.filter(Q(owners=request.user) | Q(tenants=request.user))
        serializer = property_serializers.ListMyPropertiesSerializer(qs, many=True)
        return Response({"details": serializer.data}, status=status.HTTP_200_OK)

    @action(
        methods=['GET'],
        detail=False,
        url_path='list-managed-properties'
    )
    def list_managed_properties(self, request):
        qs = property_models.Property.objects.filter(managers=request.user)
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
        date_from = request.query_params.get('date_from', None)
        date_to = request.query_params.get('date_to', None)

        filter_params = {
            Q(property__owners=request.user) | Q(property__tenants=request.user)
        }

        if date_to and date_from:
            if date_from > date_to:
                return Response({"details": "Invalid date range"}, status=status.HTTP_400_BAD_REQUEST)
            filter_params.add(Q(date_paid__range=[date_from, date_to]))

        elif date_from:
            filter_params.add(Q(date_paid__gte=date_from))

        elif date_to:
            filter_params.add(Q(date_paid__lte=date_to))

        if filter_type:
            if filter_type not in ['paid', 'unpaid', 'overdue']:
                return Response({"details": "Invalid filter type"}, status=status.HTTP_400_BAD_REQUEST)
            filter_params.add(Q(rent_status=filter_type))

        if property_id:
            try:
                instance = property_models.Property.objects.get(id=property_id)
            except property_models.Property.DoesNotExist:
                return Response({"details": "Property does not exist"}, status=status.HTTP_400_BAD_REQUEST)

            if not instance.owners.filter(id=request.user.id).exists() and not instance.tenants.filter(
                    id=request.user.id).exists() and not instance.managers.filter(id=request.user.id).exists():
                return Response({"details": "You are not an owner, tenant or manager of this property"},
                                status=status.HTTP_400_BAD_REQUEST)
            filter_params.add(Q(property=instance))

        qs = property_models.PropertyRent.objects.filter(
            *filter_params)

        serializer = property_serializers.ListPropertyRentSerializer(qs, many=True)
        return Response({"details": serializer.data}, status=status.HTTP_200_OK)

    @action(
        methods=['GET'],
        detail=False,
        url_path='list-expenses'
    )
    def list_expenses(self, request):
        # with date filters and property filters
        # general, specific
        property_id = request.query_params.get('property_id', None)
        filter_type = request.query_params.get('filter', None)
        date_from = request.query_params.get('date_from', None)
        date_to = request.query_params.get('date_to', None)

        filter_params = {
            Q(property__owners=request.user) | Q(property__tenants=request.user)
        }

        if date_to and date_from:
            if date_from > date_to:
                return Response({"details": "Invalid date range"}, status=status.HTTP_400_BAD_REQUEST)
            filter_params.add(Q(date_incurred__range=[date_from, date_to]))

        elif date_from:
            filter_params.add(Q(date_incurred__gte=date_from))

        elif date_to:
            filter_params.add(Q(date_incurred__lte=date_to))

        if filter_type:
            if filter_type not in ['general', 'incurred']:
                return Response({"details": "Invalid filter type"}, status=status.HTTP_400_BAD_REQUEST)
            filter_params.add(Q(expense_type=filter_type))

        if property_id:
            try:
                instance = property_models.Property.objects.get(id=property_id)
            except property_models.Property.DoesNotExist:
                return Response({"details": "Property does not exist"}, status=status.HTTP_400_BAD_REQUEST)

            if not instance.owners.filter(id=request.user.id).exists() and not instance.tenants.filter(
                    id=request.user.id).exists() and not instance.managers.filter(id=request.user.id).exists():
                return Response({"details": "You are not an owner, tenant or manager of this property"},
                                status=status.HTTP_400_BAD_REQUEST)
            filter_params.add(Q(property=instance))

        qs = property_models.PropertyExpense.objects.filter(
            *filter_params)

        serializer = property_serializers.ListPropertyExpenseSerializer(qs, many=True)
        return Response({"details": serializer.data}, status=status.HTTP_200_OK)

    @action(
        methods=['GET'],
        detail=False,
        url_path='list-other-receipts'
    )
    def list_other_receipts(self, request):
        property_id = request.query_params.get('property_id', None)
        date_from = request.query_params.get('date_from', None)
        date_to = request.query_params.get('date_to', None)

        filter_params = {
            Q(property__owners=request.user) | Q(property__tenants=request.user)
        }

        if date_to and date_from:
            if date_from > date_to:
                return Response({"details": "Invalid date range"}, status=status.HTTP_400_BAD_REQUEST)
            filter_params.add(Q(date_incurred__range=[date_from, date_to]))

        elif date_from:
            filter_params.add(Q(date_incurred__gte=date_from))

        elif date_to:
            filter_params.add(Q(date_incurred__lte=date_to))

        if property_id:
            try:
                instance = property_models.Property.objects.get(id=property_id)
            except property_models.Property.DoesNotExist:
                return Response({"details": "Property does not exist"}, status=status.HTTP_400_BAD_REQUEST)

            if not instance.owners.filter(id=request.user.id).exists() and not instance.tenants.filter(
                    id=request.user.id).exists() and not instance.managers.filter(id=request.user.id).exists():
                return Response({"details": "You are not an owner, tenant or manager of this property"},
                                status=status.HTTP_400_BAD_REQUEST)
            filter_params.add(Q(property=instance))

        qs = property_models.OtherReceipts.objects.filter(
            *filter_params)

        serializer = property_serializers.ListOtherReceiptsSerializer(qs, many=True)
        return Response({"details": serializer.data}, status=status.HTTP_200_OK)

    @staticmethod
    def expenses_rent_validator(request):
        property_type = request.query_params.get('property_type', None)
        property_id = request.query_params.get('property_id', None)

        filter_params = {
            Q(property__owners=request.user) | Q(property__tenants=request.user) |
            Q(property__managers=request.user)
        }

        if property_type:
            if property_type not in ['rented', 'owned']:
                return False, "Invalid property type"

            if property_type == 'rented':
                filter_params = {
                    Q(property__tenants=request.user)
                }
            else:
                filter_params = {
                    Q(property__owners=request.user)
                }

        if property_id:
            try:
                instance = property_models.Property.objects.get(id=property_id)
            except property_models.Property.DoesNotExist:
                return False, "Property does not exist"

            if not instance.owners.filter(id=request.user.id).exists() and not instance.tenants.filter(
                    id=request.user.id).exists() and not instance.managers.filter(id=request.user.id).exists():
                return False, "You are not an owner, tenant or manager of this property"

            filter_params.add(Q(property=instance))

        return True, filter_params

    @action(
        methods=['GET'],
        detail=False,
        url_path='get-total-expenses'
    )
    def get_total_expenses(self, request):
        status_code, resp = self.expenses_rent_validator(request)

        if not status_code:
            return Response({"details": resp}, status=status.HTTP_400_BAD_REQUEST)

        total_expenses = property_models.PropertyExpense.objects. \
            filter(*resp).aggregate(total=Sum('amount')).get('total')

        return Response({"details": total_expenses}, status=status.HTTP_200_OK)

    @action(
        methods=['GET'],
        detail=False,
        url_path='get-total-other-receipts'
    )
    def get_total_other_receipts(self, request):
        status_code, resp = self.expenses_rent_validator(request)

        if not status_code:
            return Response({"details": resp}, status=status.HTTP_400_BAD_REQUEST)

        total_other_receipts = property_models.OtherReceipts.objects. \
            filter(*resp).aggregate(total=Sum('amount')).get('total')

        return Response({"details": total_other_receipts}, status=status.HTTP_200_OK)

    @action(
        methods=['GET'],
        detail=False,
        url_path='get-total-rent'
    )
    def get_total_rent(self, request):
        status_code, resp = self.expenses_rent_validator(request)

        if not status_code:
            return Response({"details": resp}, status=status.HTTP_400_BAD_REQUEST)

        total_rent = property_models.PropertyRent.objects. \
            filter(*resp, rent_status="paid").aggregate(total=Sum('amount_paid')).get('total')

        return Response({"details": total_rent}, status=status.HTTP_200_OK)

    @action(
        methods=['GET'],
        detail=False,
        url_path='item-counter'
    )
    def item_counter(self, request):
        status_code, resp = self.expenses_rent_validator(request)

        if not status_code:
            return Response({"details": resp}, status=status.HTTP_400_BAD_REQUEST)

        filter_type = request.query_params.get('filter', None)

        if not filter_type or filter_type not in ['rent', 'expense', 'other_receipts']:
            return Response({"details": "Invalid filter type"}, status=status.HTTP_400_BAD_REQUEST)

        if filter_type == 'rent':
            counter = property_models.PropertyRent.objects.filter(*resp).count()
        elif filter_type == 'expense':
            counter = property_models.PropertyExpense.objects.filter(*resp).count()
        else:
            counter = property_models.OtherReceipts.objects.filter(*resp).count()

        return Response({"details": counter}, status=status.HTTP_200_OK)
