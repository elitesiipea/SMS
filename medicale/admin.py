from django.contrib import admin
from .models import DossierMedical, Consultation

@admin.register(DossierMedical)
class DossierMedicalAdmin(admin.ModelAdmin):
    list_display = ('etudiant','created', 'date_update',)
    fieldsets = (
        ('Étudiant', {
            'fields': ('etudiant',),
        }),
        ('Antécédents', {
            'fields': (
                ('hta', 'diabete', 'asthme', 'drepanocytose', 'ulcere', 'epilepsie', 'autre_antecedents'),
                
            ),
        }),
        ('Antécédents Mère', {
            'fields': (
               
                ('mere_hta', 'mere_diabete', 'mere_asthme', 'mere_drepanocytose', 'mere_ulcere', 'mere_epilepsie', 'mere_autre_antecedents'),
            ),
        }),
        ('Antécédents Père', {
            'fields': (
               
                ('pere_hta', 'pere_diabete', 'pere_asthme', 'pere_drepanocytose', 'pere_ulcere', 'pere_epilepsie', 'pere_autre_antecedents'),
             
            ),
        }),
        ('État de vie', {
            'fields': ('tabac', 'alcool', 'stupefiant'),
        }),
    )
    # Autres options d'administration

@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Dossier', {
            'fields': ('dossier','medecin','annee_academique'),
        }),
        ('Constantes', {
            'fields': ('TA', 'pouls', 'Temperature', 'FR', 'Sao2', 'Glasgow'),
        }),
        ('Données', {
            'fields': (
                'motif_de_la_consultation', 'histoire_de_la_mamdie', 'examen_physique',
                'hypotheses_diagnostic', 'examens_paracliniques', 'diagnostic_retenu', 'traitement', 'evolution',
            ),
        }),
        ('Arrêt Maladie', {
            'fields': ('rendez_vous', 'arret_de_travail', 'debut_arret_travail', 'fin_arret_travail'),
        }),
    )
    # Autres options d'administration
