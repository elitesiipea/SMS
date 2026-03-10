# transport_app/admin.py

from django.contrib import admin
from .models import Car, Trajet, Abonnement, Paiement

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('immatriculation', 'nombre_places')

@admin.register(Trajet)
class TrajetAdmin(admin.ModelAdmin):
    list_display = ('depart', 'arrive', 'cout_mensuel')

@admin.register(Abonnement)
class AbonnementAdmin(admin.ModelAdmin):
    list_display = ('etudiant', 'trajet', 'from_date', 'to_date')
    
@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ('abonnement', 'montant', 'wave_launch_url', 'wave_id')
