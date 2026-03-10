import os
# dev.py
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
# Importez les paramètres communs du fichier settings.py
from ..settings import *

# Activez le mode de débogage pour l'environnement de développement
DEBUG = True

# Ajoutez ici vos configurations spécifiques pour l'environnement de développement
# Par exemple, vous pouvez utiliser une base de données SQLite différente pour le développement


ALLOWED_HOSTS = ['*']

DATABASES = {

       "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "db2",
        "USER": "postgres",
        "PASSWORD": "10027563",
        "HOST": "127.0.0.1",
        "PORT": "5432",
    }

}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_DIR = os.path.join(BASE_DIR, 'staticfiles')
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_DIR = os.path.join(BASE_DIR, 'media')
MEDIA_ROOT = MEDIA_DIR
MEDIA_URL = '/media/'
STATIC_URL = '/staticfiles/'

# Vous pouvez également ajouter d'autres configurations spécifiques au développement ici
