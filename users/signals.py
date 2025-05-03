from django.dispatch import receiver
from django.urls import reverse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django_rest_passwordreset.signals import reset_password_token_created
from django.conf import settings
from django.db.models.signals import post_save, post_delete
from .models import User

@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    """
    # Send email with the reset token
    context = {
        'current_user': reset_password_token.user,
        'full_name': reset_password_token.user.full_name,
        'email': reset_password_token.user.email,
        'reset_password_url': f"{instance.request.scheme}://{instance.request.get_host()}{reverse('users:password_reset_confirm_page')}?token={reset_password_token.key}",
        'site_name': 'UniBazzar',
    }

    # Render email templates
    email_html_message = render_to_string('users/email_reset_password.html', context)
    email_plaintext_message = render_to_string('users/email_reset_password.txt', context)

    # Send email
    msg = EmailMultiAlternatives(
        subject="Password Reset for UniBazzar",
        body=email_plaintext_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[reset_password_token.user.email]
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()

# Removed Supabase sync signal handler
# @receiver(post_save, sender=User)
# def sync_user_to_supabase(sender, instance, created, **kwargs):
#     ...

# Removed Supabase delete signal handler
# @receiver(post_delete, sender=User)
# def delete_user_from_supabase(sender, instance, **kwargs):
#     ... 