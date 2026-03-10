from django.urls import path, include
from . import views


urlpatterns = [
    path('times_list/', views.emploi_du_temps_list,name="emploi_du_temps_list"),
    path('times_list/emargements/', views.emargements,name="emargements"),
    path('emploisdutemps/<int:emploisdutemps_id>/?edit=<slug:edit>/', views.emploisdutemps_detail, name='emploisdutemps_detail'),
    path('programme/<int:programme_id>/delete/', views.delete_programme, name='delete_programme'),

    
   
]