from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework import exceptions
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

class SupabaseJWTAuthentication(BaseAuthentication):
    """
    DRF authentication class using Supabase JWT.
    Expects the token to be provided in the Authorization header as 'Bearer <token>'.
    """
    keyword = 'Bearer'

    def authenticate(self, request):
        """
        Authenticates the request by extracting and validating the Supabase JWT.
        """
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            # No Authorization header with 'Bearer' keyword
            return None # No authentication attempt

        if len(auth) == 1:
            msg = _('Invalid bearer header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid bearer header. Token string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = _('Invalid bearer header. Token string should not contain invalid characters.')
            raise exceptions.AuthenticationFailed(msg)

        # Delegate the actual token validation and user retrieval to Django's
        # authenticate function, which will call our SupabaseAuthBackend.
        user = authenticate(request=request, access_token=token)

        if user is None:
            # authenticate() returns None if validation fails in the backend
            raise exceptions.AuthenticationFailed(_('Invalid Supabase token or user not found.'))

        # Check if the user is active
        if not user.is_active:
             raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        # For DRF, authenticate() should return a tuple (user, auth)
        # The second element (auth) is the credential itself (the token)
        return (user, token)

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        return f'{self.keyword} realm="api"' 