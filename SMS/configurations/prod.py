# prod.py

# Importez les paramètres communs du fichier settings.py
from ..settings import *

# Désactivez le mode de débogage pour l'environnement de production
DEBUG = False

# Ajoutez ici vos configurations spécifiques pour l'environnement de production
# Par exemple, vous pouvez utiliser une base de données PostgreSQL pour la production


ALLOWED_HOSTS = ['*']

DATABASES = {

       "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "db2",
        "USER": "daniel",
        "PASSWORD": "10027563",
        "HOST": "127.0.0.1",
        "PORT": "5432",
    }

}

# Vous pouvez également ajouter d'autres configurations spécifiques à la production ici



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/
STATIC_URL = "/staticfiles/"
MEDIA_ROOT = "/home/daniel/SMS/SMS/media/"
MEDIA_URL = "/media/"
STATICFILES_DIR = "/home/daniel/SMS/SMS/staticfiles/"
STATIC_ROOT = "/home/daniel/SMS/SMS/staticfiles/"