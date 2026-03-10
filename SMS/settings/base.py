import os
from pathlib import Path
from django.contrib.messages import constants as messages
from import_export.formats.base_formats import CSV, XLSX


BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.getenv('SECRET_KEY')

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')

INSTALLED_APPS = [
    # Django core
    "admin_interface",
    "colorfield",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Custom apps
    'administration', 'authentication', 'bibliotheque', 'comptabilite',
    'curriculum', 'emplois_du_temps', 'enseignant', 'etudiants',
    'evaluations', 'gestion_academique', 'inscription', 'parents',
    'ressources_humaines', 'medicale', 'notification', 'transport',
    'personnel', 'ajax_select', 'gestion_stock',

    # Third-party
    'cloudinary', 'cloudinary_storage',
    'crispy_forms', 'crispy_bootstrap4',
    'django_countries', 'import_export', 'drf_yasg',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'SMS.urls'
WSGI_APPLICATION = 'SMS.wsgi.application'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]

LANGUAGE_CODE = 'fr-FR'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'authentication.User'

LOGIN_URL = 'login'
LOGOUT_URL = 'logout'
LOGIN_REDIRECT_URL = 'redirection'
LOGOUT_REDIRECT_URL = 'login'

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap4'
CRISPY_TEMPLATE_PACK = 'bootstrap4'
BOOTSTRAP4 = {'include_jquery': True}

IMPORT_FORMATS = [CSV, XLSX]
EXPORT_FORMATS = [XLSX]

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")
X_FRAME_OPTIONS = 'SAMEORIGIN'
SILENCED_SYSTEM_CHECKS = ['security.W019']

# Patch django_countries for compatibility
from django_countries.widgets import LazyChoicesMixin

# Définir la méthode get_choices
def get_choices(self):
    return self._choices

# Définir la méthode set_choices
def set_choices(self, value):
    self._choices = value

# Appliquer le patch
LazyChoicesMixin.get_choices = get_choices
LazyChoicesMixin.set_choices = set_choices
LazyChoicesMixin.choices = property(LazyChoicesMixin.get_choices, LazyChoicesMixin.set_choices)

# Email
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS') == 'True'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))

SMS_DEMO_RECIPIENTS = "danielguedegbe10027@gmail.com,octogone.techs@gmail.com"

