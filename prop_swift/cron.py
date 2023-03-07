import decimal
import threading
from datetime import date
from shared_utils import notification_utils
from property.models import Property


def my_scheduled_job():
    recipient = "nelfrankaj@gmail.com"
    notification_utils.send_email(
        subject="Test email",
        message="This is a test email",
        recipient=recipient
    )

def email_handler(property_name, expense_list, email_list, rent_body=None):
    # django email template
    subject = "Property Report"
    message = f"Hello, this is a report for {property_name}.\n\n"
    message += "Expenses:\n"
    amount = 0
    for expense in expense_list:
        message += f"{expense.date_incurred}: {expense.expense_type.title()} - Ksh {expense.amount}\n"
        amount += decimal.Decimal(expense.amount)
    message += "\n\n"
    message += f"Total expenses: Ksh {amount}\n"
    if rent_body:
        message += f"Rent amount: {rent_body['rent_amount']}\n"
        message += f"Due date: {rent_body['due_date']}\n"
    message += "\n"
    message += "Regards,\n"
    message += "Property Swift"

    for email in email_list:
        notification_utils.send_email(
            subject=subject,
            message=message,
            recipient=email
        )

def reports_scheduler():
    qs = Property.objects.filter(date_due=date.today())

    for instance in qs:
        # property name
        property_name = instance.name

        # retrieve expense list
        expense_list = instance.property_expenses.filter(
            date_incurred__month=date.today().month
        ).order_by("date_incurred")


        # send email to the owner
        if instance.owners.exists() or instance.managers.exists():
            email_list = instance.owners.values_list('username', flat=True)
            email_list.extend(instance.managers.values_list('username', flat=True))
            threading.Thread(target=email_handler, args=(property_name, expense_list, email_list),
                             daemon=False).start()

        if instance.tenants.exists():
            email_list = instance.tenants.values_list('username', flat=True)

            # rent amount for property
            rent_amount = instance.rent_amount
            rent_body = {"rent_amount": rent_amount, "due_date": instance.date_due}
            threading.Thread(target=email_handler, args=(property_name, expense_list, email_list, rent_body),
                                daemon=False).start()









