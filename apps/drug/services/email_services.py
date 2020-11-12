from django.conf import settings
from django.core.mail import EmailMessage


class EmailService:

    @staticmethod
    def send_email(subject, msg_html, recipient_list: [str]):
        email_from = settings.DJANGO_DEFAULT_FROM_EMAIL
        msg = EmailMessage(subject=subject, body=msg_html, from_email=email_from, to=recipient_list)
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()
