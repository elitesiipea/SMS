import os

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-!12i9#d%2so^p$z(&_^$xa*9!i%8=j#a#2lw391=ala1u7kh7w'

CSRF_TRUSTED_ORIGINS = ['https://myiipea.com','http://myiipea.com']

X_FRAME_OPTIONS = "SAMEORIGIN"

SILENCED_SYSTEM_CHECKS = ["security.W019"]

DEBUG = False

if DEBUG:
    
    # Utilisez les paramètres de développement192.168.1.25:8000
    from .configurations.dev import *
    
else:
    # Utilisez les paramètres de production
    from .configurations.prod import *

# import sentry_sdk

# from sentry_sdk.integrations.django import DjangoIntegration

# sentry_sdk.init(
#     dsn="https://eb0df07d5fa040aaa4b4cfd844e02909@o4504797949591552.ingest.sentry.io/4504797951361024",
#     integrations=[
#         DjangoIntegration(),
#     ],

#     # Set traces_sample_rate to 1.0 to capture 100%
#     # of transactions for performance monitoring.
#     # We recommend adjusting this value in production.
#     traces_sample_rate=1.0,

#     # If you wish to associate users to errors (assuming you are using
#     # django.contrib.auth) you may enable sending PII data.
#     send_default_pii=True
# )


# Application definition
# Our Installed Application definition
from .configurations.app import *

# # Cloudinary Files Managemnet
# from .configurations.cloudinary import *

from .configurations.base import *

from .configurations.email import *




LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}