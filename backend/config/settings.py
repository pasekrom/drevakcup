"""
Django settings for drevakcup backend API.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-me-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = [
    h.strip() for h in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if h.strip()
]

# Veřejná URL webu (https://… bez koncového /). Pro správné odkazy na /static/team_flags/… v JSON (vlajky),
# když je Django za proxy a request.build_absolute_uri dává špatný host nebo http.
SITE_PUBLIC_URL = os.getenv('SITE_PUBLIC_URL', '').strip().rstrip('/')


def _split_origins(env_key, defaults):
    """Čárkou oddělené URL se schématem (např. https://example.cz)."""
    raw = os.getenv(env_key, '').strip()
    extra = [o.strip() for o in raw.split(',') if o.strip()]
    seen = set()
    out = []
    for o in defaults + extra:
        if o not in seen:
            seen.add(o)
            out.append(o)
    return out


# CSRF: musí obsahovat přesný Origin prohlížeče (schéma + host, bez cesty) — jinak POST/login selže v produkci.
CSRF_TRUSTED_ORIGINS = _split_origins(
    'CSRF_TRUSTED_ORIGINS',
    [
        'http://localhost:5173',
        'http://127.0.0.1:5173',
        'http://localhost:3000',
        'http://127.0.0.1:3000',
    ],
)


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'drf_spectacular',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database: use SQLite for local dev when USE_SQLITE=1 (no PostgreSQL needed)
if os.getenv('USE_SQLITE', '').strip().lower() in ('1', 'true', 'yes'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'drevakcup'),
            'USER': os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    }


# Password validation
AUTH_USER_MODEL = 'api.User'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'cs'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# URL vždy začíná /static/… — v nginx musí být location /static/ (ne jen /static/django/), viz deploy/nginx-site.example.conf
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        # Keycloak authentication will be added here when configured
        # 'api.authentication.KeycloakAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# CORS: v produkci doplň stejnou veřejnou URL frontendu jako v CSRF_TRUSTED_ORIGINS (proměnná CORS_ALLOWED_ORIGINS).
CORS_ALLOWED_ORIGINS = _split_origins(
    'CORS_ALLOWED_ORIGINS',
    [
        'http://localhost:5173',
        'http://localhost:3000',
        'http://127.0.0.1:5173',
        'http://127.0.0.1:3000',
    ],
)

CORS_ALLOW_CREDENTIALS = True

# Keycloak configuration (for future use)
KEYCLOAK_SERVER_URL = os.getenv('KEYCLOAK_SERVER_URL', '')
KEYCLOAK_REALM = os.getenv('KEYCLOAK_REALM', '')
KEYCLOAK_CLIENT_ID = os.getenv('KEYCLOAK_CLIENT_ID', '')
KEYCLOAK_CLIENT_SECRET = os.getenv('KEYCLOAK_CLIENT_SECRET', '')

# API Documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'Drevak Cup API',
    'DESCRIPTION': 'IIHF Tournament Prediction Platform API',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}
