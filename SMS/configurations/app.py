INSTALLED_APPS = [
    "admin_interface",
    "colorfield",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
     'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.staticfiles',

]

INSTALLED_APPS += [

    'administration',
    'authentication',
    'bibliotheque',
    'comptabilite',
    'curriculum',
    'emplois_du_temps',
    'enseignant',
    'etudiants',
    'evaluations',
    'gestion_academique',
    'inscription',
    'parents',
    'ressources_humaines',
    'cloudinary', # For file management
    'cloudinary_storage', # For file management
    "crispy_forms", #   Crispy Forms
    "crispy_bootstrap4",
    'django_countries',
    'import_export',# Import Export
    'medicale',
    'notification',
    'drf_yasg',
    'transport',
    'personnel',
    'ajax_select',
    'gestion_stock',
    #
  
    
    
    
]

X_FRAME_OPTIONS = "SAMEORIGIN"
SILENCED_SYSTEM_CHECKS = ["security.W019"]