import jwt
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

# Add email authentication handling:

class EmailBackend:
    """
    Authenticate against django.contrib.auth.models.User using email.
    """
    def authenticate(self, request, email=None, password=None, **kwargs):
        from django.contrib.auth import get_user_model
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=email)
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            return None
        except Exception as e:
            return None

    def get_user(self, user_id):
        from django.contrib.auth import get_user_model
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None