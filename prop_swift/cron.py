from shared_utils import notification_utils


def my_scheduled_job():
    recipient = "nelfrankaj@gmail.com"
    notification_utils.send_email(
        subject="Test email",
        message="This is a test email",
        recipient=recipient
    )
