"""Celery tasks for notifications and emails"""
from celery import shared_task
import logging

logger = logging.getLogger('scm')


@shared_task(name='notifications.tasks.send_notification_email')
def send_notification_email(notification_id):
    from notifications.models import Notification
    from django.core.mail import send_mail
    from django.conf import settings
    try:
        notif = Notification.objects.select_related('recipient').get(id=notification_id)
        send_mail(
            subject=f'[SCM] {notif.title}',
            message=notif.message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[notif.recipient.email],
            fail_silently=False,
        )
        logger.info(f"Email sent: {notif.title} → {notif.recipient.email}")
    except Exception as e:
        logger.error(f"Email send failed: {e}")


@shared_task(name='notifications.tasks.send_password_reset_email')
def send_password_reset_email(user_id, token):
    from django.contrib.auth import get_user_model
    from django.core.mail import send_mail
    from django.conf import settings
    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
        reset_url = f"http://localhost:8000/accounts/reset-password/{token}/"
        send_mail(
            subject='Password Reset Request - FlowChain',
            message=f'Hi {user.first_name},\n\nClick below to reset your password:\n{reset_url}\n\nThis link expires in 24 hours.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Password reset email failed: {e}")


@shared_task(name='notifications.tasks.send_invoice_email')
def send_invoice_email(invoice_id):
    from sales.models import Invoice
    from django.core.mail import EmailMessage
    from django.conf import settings
    try:
        invoice = Invoice.objects.select_related('customer').get(id=invoice_id)
        msg = EmailMessage(
            subject=f'Invoice #{invoice.invoice_number} - {settings.COMPANY_NAME}',
            body=f'Dear {invoice.customer.name},\n\nPlease find your invoice attached.\n\nAmount Due: ₹{invoice.balance_due:,.2f}\nDue Date: {invoice.due_date}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[invoice.customer.email],
        )
        if invoice.pdf_file:
            msg.attach_file(invoice.pdf_file.path)
        msg.send()
        logger.info(f"Invoice email sent: INV-{invoice.invoice_number}")
    except Exception as e:
        logger.error(f"Invoice email failed: {e}")
