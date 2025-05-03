from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage, get_connection
from django.conf import settings
from .tokens import email_verification_token
import os
import uuid
import socket
import logging

# Set up logging
logger = logging.getLogger(__name__)

def send_verification_email(user, request):
    """
    Send email verification link to the user
    """
    try:
        # Get site info
        try:
            current_site = get_current_site(request)
            site_name = current_site.name
        except Exception as e:
            logger.warning(f"Error getting site info: {str(e)}")
            site_name = "UniBazzar"
        
        mail_subject = 'Activate your UniBazzar account'
        
        # Generate token
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = email_verification_token.make_token(user)
        
        # Determine domain and scheme
        if settings.DEBUG:
            domain = "localhost:8000"  # Always use localhost:8000 in debug mode
            scheme = "http"
        else:
            domain = current_site.domain
            scheme = request.scheme
        
        # Create verification link
        if settings.DEBUG:
            # Always use localhost:8000 in debug mode
            verification_link = f"http://localhost:8000/api/users/verify-email/{uid}/{token}/"
        else:
            verification_link = f"{scheme}://{domain}/api/users/verify-email/{uid}/{token}/"
            
        logger.info(f"Generated verification link: {verification_link}")
        
        # Prepare email content
        try:
            message = render_to_string('users/email_verification.html', {
                'user': user,
                'verification_link': verification_link,
                'site_name': site_name,
            })
        except Exception as e:
            logger.warning(f"Template rendering error: {str(e)}")
            # Fallback to a simple plain text message
            message = f"""
            Hello {user.full_name},
            
            Please verify your email by clicking the link below:
            {verification_link}
            
            This link will expire in 24 hours.
            
            Thanks,
            The UniBazzar Team
            """
        
        # Send email via SMTP
        try:
            # Log SMTP details for debugging (don't include password)
            logger.info(f"Sending email via SMTP: Host={settings.EMAIL_HOST}, Port={settings.EMAIL_PORT}, "
                  f"TLS={settings.EMAIL_USE_TLS}, From={settings.EMAIL_HOST_USER}")
            
            # Check network connectivity to the SMTP server
            try:
                socket.create_connection((settings.EMAIL_HOST, settings.EMAIL_PORT), timeout=5)
                logger.info(f"Network connection to {settings.EMAIL_HOST}:{settings.EMAIL_PORT} successful")
            except (socket.timeout, socket.error) as e:
                logger.error(f"Network connection to {settings.EMAIL_HOST}:{settings.EMAIL_PORT} failed: {str(e)}")
                
                # Fall back to console backend if we can't connect
                if settings.DEBUG:
                    logger.info("Falling back to console email backend")
                    
                    # Use the fallback email backend
                    fallback_connection = get_connection(
                        backend=settings.FALLBACK_EMAIL_BACKEND,
                    )
                    
                    fallback_email = EmailMessage(
                        mail_subject,
                        message,
                        from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@unibazzar.com',
                        to=[user.email],
                        connection=fallback_connection
                    )
                    fallback_email.content_subtype = "html"
                    fallback_email.send(fail_silently=True)
                    
                    return True  # Return True for development convenience
                return False
            
            # Get connection with timeout
            connection = get_connection(
                backend=settings.EMAIL_BACKEND,
                host=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                username=settings.EMAIL_HOST_USER,
                password=settings.EMAIL_HOST_PASSWORD,
                use_tls=settings.EMAIL_USE_TLS,
                timeout=10
            )
            
            email = EmailMessage(
                mail_subject, 
                message, 
                from_email=settings.EMAIL_HOST_USER,
                to=[user.email],
                connection=connection
            )
            email.content_subtype = "html"
            
            # Send the email and get the result
            result = email.send(fail_silently=False)
            
            if result == 1:
                logger.info(f"Email sent successfully to {user.email}")
                return True
            else:
                logger.error(f"Failed to send email. Result: {result}")
                return False
                
        except Exception as e:
            logger.error(f"SMTP Error: {str(e)}")
            
            if settings.DEBUG:
                # In debug mode, use the fallback email backend
                logger.info(f"Using fallback email backend (console) after SMTP error")
                
                try:
                    fallback_connection = get_connection(
                        backend=settings.FALLBACK_EMAIL_BACKEND,
                    )
                    
                    fallback_email = EmailMessage(
                        mail_subject,
                        message,
                        from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@unibazzar.com',
                        to=[user.email],
                        connection=fallback_connection
                    )
                    fallback_email.content_subtype = "html"
                    fallback_email.send(fail_silently=True)
                    
                except Exception as fallback_error:
                    logger.error(f"Fallback email error: {str(fallback_error)}")
                
                return True  # Return True for development convenience
            return False
            
    except Exception as e:
        logger.error(f"Error sending verification email: {str(e)}")
        return False

def get_unique_filename(instance, filename):
    """
    Generate a unique filename for uploaded files
    """
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('profile_pictures', filename)

def validate_password_strength(password):
    """
    Validate password strength - Currently disabled for development
    """
    # All validations disabled for development
    return True, "Password is valid."

