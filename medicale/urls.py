from django.urls import path, include
from .views import (dossier_medical_views, consultation_create, consultation_details, dossier_update, consultation_list)

urlpatterns = [

    path("dossier/", dossier_medical_views,name="dossier_medical_views"),
    path("consultation_create/<int:pk>/<slug:code>/?consultatioon=<slug:consultation_id>/", consultation_create,name="consultation_create"),
    path("consultation_details/<int:pk>/<slug:code>/<int:dossier>/", consultation_details,name="consultation_details"),
    path("update_dossier/<int:pk>/", dossier_update,name="dossier_update"),
    path("consultation_list/", consultation_list,name="consultation_list"),

    
    

]