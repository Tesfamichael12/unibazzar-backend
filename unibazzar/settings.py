import os
from pathlib import Path
from dotenv import load_dotenv
from decouple import config
from datetime import timedelta
# import dj_database_url # Only needed if you use dj_database_url for database config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file from the BASE_DIR (project root)
ENV_PATH = BASE_DIR / '.env'
load_dotenv(dotenv_path=ENV_PATH)
# print(f"DEBUG: Attempted to load .env file from: {ENV_PATH}")
# print(f"DEBUG: Value of GEMINI_API_KEY from os.environ after load_dotenv: {os.getenv('GEMINI_API_KEY')}")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

# Gemini API Key - Load directly from os.environ now
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
# print(f"DEBUG: GEMINI_API_KEY assigned in settings: '{GEMINI_API_KEY}'")

if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY not found in environment variables or is empty. Chatbot functionality will be disabled.")
# else:
    # print(f"INFO: GEMINI_API_KEY loaded in settings: '{GEMINI_API_KEY[:5]}...'")

ALLOWED_HOSTS_str = config('ALLOWED_HOSTS', default='127.0.0.1,localhost')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_str.split(',')]


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites', # Required by allauth

    # Third-party apps
    'corsheaders',
    'rest_framework',
    # 'rest_framework.authtoken', # IMPORTANT: Ensure this is commented out or removed
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist', # If you use blacklist functionality

    'allauth',                  # Moved up
    'allauth.account',          # Moved up
    'allauth.socialaccount',    # Moved up

    'dj_rest_auth',
    'dj_rest_auth.registration', # If you use dj_rest_auth's registration views
    'drf_yasg',
    'django_rest_passwordreset',
    # 'allauth.socialaccount.providers.google', # Add specific providers if you use them

    # Local apps
    'users',
    'products',
    'chatbot',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware', # For allauth
]

ROOT_URLCONF = 'unibazzar.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # `allauth` needs this from django
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'unibazzar.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
print("INFO: Forcing SQLite database configuration.") # Indicate SQLite is being used

# If you plan to use Supabase or another Postgres DB, configure it here or via DATABASE_URL
# The following block is INTENTIONALLY COMMENTED OUT to force SQLite usage for now,
# regardless of what is in the .env file for DATABASE_URL.
#
# DATABASE_URL_FROM_ENV = config('DATABASE_URL', default=None)
# if DATABASE_URL_FROM_ENV:
#     print(f"INFO: DATABASE_URL found: '{DATABASE_URL_FROM_ENV[:15]}...' (currently bypassed)")
#     # try:
#     #     import dj_database_url
#     #     DATABASES['default'] = dj_database_url.parse(DATABASE_URL_FROM_ENV, conn_max_age=600)
#     #     print("INFO: Successfully configured database using DATABASE_URL.")
#     # except ValueError as e:
#     #     print(f"WARNING: DATABASE_URL is set but invalid ('{DATABASE_URL_FROM_ENV}'). Error: {e}. Falling back to SQLite.")
#     # except ImportError:
#     #     print("WARNING: dj_database_url is not installed. DATABASE_URL will be ignored. Falling back to SQLite.")
# else:
#     # This branch would be hit if DATABASE_URL was not in .env at all
#     print("INFO: DATABASE_URL not found in environment. Using default SQLite database.")


AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Authentication Backends
AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
    # Custom backend for email-based authentication (if 'users.backends.EmailBackend' exists and is used)
    # 'users.backends.EmailBackend', # Uncomment if you have this custom backend
)


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_build', 'static') # For collectstatic
# STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')] # If you have app-specific static files not in app/static/
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'users.User'
SITE_ID = 1 # Required by allauth and sites framework

# REST Framework Settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    # 'DEFAULT_SCHEMA_CLASS': 'drf_yasg.inspectors.SwaggerAutoSchema', # Temporarily comment out
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.openapi.AutoSchema', # Try DRF's default AutoSchema
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# dj-rest-auth Settings
REST_AUTH = {
    'USE_JWT': True,
    'JWT_AUTH_HTTPONLY': False, # True means JWT is stored in httpOnly cookie, JS can't access.
                                # False means JWT is returned in response body, JS can access.
    'JWT_AUTH_COOKIE': None, # Name of the cookie to store the JWT if JWT_AUTH_HTTPONLY is True
    'JWT_AUTH_REFRESH_COOKIE': None, # Name of the refresh JWT cookie
    'SESSION_LOGIN': False, # Set to False if you only want JWT based auth and not session login via dj_rest_auth views
    'USER_DETAILS_SERIALIZER': 'users.serializers.UserProfileSerializer', # Corrected path
    'REGISTER_SERIALIZER': 'users.serializers.UserRegistrationSerializer', # Corrected to existing serializer
    'TOKEN_MODEL': None, # Explicitly tell dj_rest_auth not to use the default authtoken.Token model
    # Add other dj_rest_auth settings as needed
}

# Simple JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=config('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', default=60, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=config('JWT_REFRESH_TOKEN_LIFETIME_DAYS', default=7, cast=int)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=config('JWT_SLIDING_TOKEN_LIFETIME_MINUTES', default=5, cast=int)),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=config('JWT_SLIDING_TOKEN_REFRESH_LIFETIME_DAYS', default=1, cast=int)),
}

# CORS Settings
CORS_ALLOWED_ORIGINS_STR = config('CORS_ALLOWED_ORIGINS', default="http://localhost:3000,http://127.0.0.1:3000")
CORS_ALLOWED_ORIGINS_LIST = CORS_ALLOWED_ORIGINS_STR.split(',')
# Clean up escaped colons and remove trailing slashes
CORS_ALLOWED_ORIGINS = [
    url.replace('\\x3a', ':').replace('\\:', ':').rstrip('/') 
    for url in CORS_ALLOWED_ORIGINS_LIST
]
CORS_ALLOW_CREDENTIALS = True

# Email settings
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)
FALLBACK_EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_TIMEOUT = config('EMAIL_TIMEOUT', default=5, cast=int)

# Password Reset (django-rest-passwordreset)
DJANGO_REST_PASSWORDRESET_TOKEN_CONFIG = {
    "CLASS": "django_rest_passwordreset.tokens.RandomStringTokenGenerator",
    "OPTIONS": {
        "min_length": config('PASSWORD_RESET_TOKEN_MIN_LENGTH', default=20, cast=int),
        "max_length": config('PASSWORD_RESET_TOKEN_MAX_LENGTH', default=30, cast=int)
    }
}
# This setting is for a different library (django-rest-multitokenauth), not django-rest-passwordreset
# DJANGO_REST_MULTITOKENAUTH_RESET_TOKEN_EXPIRY_TIME = int(os.environ.get('PASSWORD_RESET_TOKEN_EXPIRY_HOURS', '24'))
# For django-rest-passwordreset, the expiry is handled by a periodic cleanup command or by checking token age.

# django-allauth settings
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False # Or True, depending on your needs
ACCOUNT_USER_MODEL_USERNAME_FIELD = None # Explicitly set to None for email-only auth
ACCOUNT_AUTHENTICATION_METHOD = 'email' # Or 'username' or 'username_email'
ACCOUNT_EMAIL_VERIFICATION = 'optional' # 'mandatory' or 'none'
LOGIN_REDIRECT_URL = '/' # Or your frontend URL
LOGOUT_REDIRECT_URL = '/' # Or your frontend URL
ACCOUNT_ADAPTER = 'users.adapter.CustomAccountAdapter' # If you have a custom adapter
SOCIALACCOUNT_ADAPTER = 'users.adapter.CustomSocialAccountAdapter' # If you have a custom social adapter
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'APP': { # If you store client_id and secret in DB via SocialApp model
            # 'client_id': 'your-google-client-id',
            # 'secret': 'your-google-client-secret',
            # 'key': '' # Deprecated
        }
    }
}
# If using environment variables for Google OAuth for allauth (less common for allauth, usually done via SocialApp model in admin)
# SOCIALACCOUNT_GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID', default=None)
# SOCIALACCOUNT_GOOGLE_CLIENT_SECRET = config('GOOGLE_CLIENT_SECRET', default=None)


# Swagger Settings (drf-yasg)
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': "JWT Token (add 'Bearer ' prefix)"
        }
    },
    'USE_SESSION_AUTH': False, # Set to False if you primarily use Token/JWT for API
    'LOGIN_URL': '/admin/login/', # Or your API login URL if not using session auth for Swagger
    'LOGOUT_URL': '/admin/logout/', # Or your API logout URL
    # ... other swagger settings from your original file
    'PERSIST_AUTH': True,
    'DOC_EXPANSION': 'list',
}

# Ensure dj_database_url is only imported if DATABASE_URL is used
# if config('DATABASE_URL', default=None):
#     import dj_database_url
#     DATABASES['default'] = dj_database_url.parse(config('DATABASE_URL'), conn_max_age=600)

# Remove the debug prints for GEMINI_API_KEY for cleaner logs once confirmed working
# print(f"DEBUG: Attempted to load .env file from: {ENV_PATH}")
# print(f"DEBUG: Value of GEMINI_API_KEY from os.environ after load_dotenv: {os.getenv('GEMINI_API_KEY')}")
# print(f"DEBUG: GEMINI_API_KEY assigned in settings: '{GEMINI_API_KEY}'")
# if GEMINI_API_KEY:
# print(f"INFO: GEMINI_API_KEY loaded in settings: '{GEMINI_API_KEY[:5]}...'")