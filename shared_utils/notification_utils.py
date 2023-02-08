from django.core.mail import send_mail


def send_email(subject, message, recipient):
    sender = ""
    send_mail(
        subject,
        message,
        sender,
        [recipient],
        fail_silently=False,
    )
