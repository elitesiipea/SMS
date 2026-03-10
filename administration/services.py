from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import DemoRequest


def send_demo_request_emails(demo: DemoRequest) -> None:
    """
    Envoie 2 e-mails :
    - un e-mail de confirmation au demandeur
    - un e-mail de notification à l'équipe OCTOGONE
    """

    # 1) Mail au prospect
    subject_user = "Votre demande de démo SMS - School Management System"
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", settings.EMAIL_HOST_USER)
    to_user = [demo.email]

    context_user = {"demo": demo}
    html_user = render_to_string("emails/demo_request_confirmation.html", context_user)

    msg_user = EmailMultiAlternatives(subject_user, "", from_email, to_user)
    msg_user.attach_alternative(html_user, "text/html")
    msg_user.send(fail_silently=False)

    # 2) Mail à l'équipe
    subject_admin = f"[SMS Demo] Nouvelle demande – {demo.school_name}"
    recipients = getattr(
        settings,
        "SMS_DEMO_RECIPIENTS",
        [from_email],
    )

    context_admin = {"demo": demo}
    html_admin = render_to_string("emails/demo_request_notification.html", context_admin)

    msg_admin = EmailMultiAlternatives(subject_admin, "", from_email, recipients)
    msg_admin.attach_alternative(html_admin, "text/html")
    msg_admin.send(fail_silently=False)
