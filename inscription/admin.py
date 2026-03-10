from django.contrib import admin
from .models import Inscription, Paiement
from gestion_academique.models import Classe, Filiere, Niveau
# Register the Inscription model
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.contrib.admin.models import LogEntry, CHANGE
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from import_export.fields import Field

@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):
    list_display = ('etudiant', 'annee_academique', 'filiere', 'niveau','classe','confirmed','solded' , 'parcour', 'frais', 'paye',
                    'polo', 'macaron', 'cravate', 'tissu','rame','marqueur','active', 'nouvel_etudiant', 'created', 
                    'date_update', 'absence_semestre1', 'absence_semestre2', 'carte_etudiant',)
    list_filter = ('annee_academique', 'filiere', 'niveau', 'parcour', 'active', 'nouvel_etudiant', 'confirmed')
    search_fields = ('etudiant__nom', 'etudiant__prenom', 'etudiant__matricule')
    readonly_fields = ('etudiant','annee_academique', 'active', 'nouvel_etudiant', 'created', 'date_update')  
    # As you calculate it automatically in the save method, it should be read-only.

    def get_queryset(self, request):
        # Récupérer l'établissement de l'utilisateur connecté
        etablissement = request.user.etablissement
        # Appeler la méthode personnalisée pour filtrer les utilisateurs
        queryset = Inscription.objects.filter(etudiant__etablissement=etablissement)
        return queryset
    
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        etablissement = request.user.etablissement
        if db_field.name == 'classe':
            if request.GET.get('niveau'):
                # Filter classes based on selected niveau
                kwargs['queryset'] = Classe.objects.filter(
                    annee_academique__etablissement=etablissement,
                    niveau=request.GET.get('niveau')
                )
            else:
                kwargs['queryset'] = Classe.objects.filter(
                    annee_academique__etablissement=etablissement,
                )
                
        if db_field.name == 'filiere':
                kwargs['queryset'] = Filiere.objects.filter(
                    etablissement=etablissement,
                )
                
        if db_field.name == 'niveau':
                kwargs['queryset'] = Niveau.objects.filter(
                    etablissement=etablissement,
                )
                # Handle the case when request.instance is None
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class PaieResource(resources.ModelResource):
    inscription = Field(column_name='Inscription')  # Rename the column

    class Meta:
        model = Paiement
        fields = ('inscription', 'montant', 'source', 'reference', 'active', 'created', 'date_update', 'confirmed')

    def dehydrate_inscription(self, paiement):
        return str(paiement.inscription)  # Return the string representation
        
# Admin class with optimizations
@admin.register(Paiement)
class PaiementAdmin(ImportExportModelAdmin):
    list_display = ('inscription', 'montant', 'source', 'reference', 'active', 'created', 'date_update', 'confirmed')
    list_display_links = ('inscription',)  # Allow editing from list view
    #list_editable = ('montant', 'source', 'reference', 'confirmed','created')  # Make fields editable inline
    search_fields = ('inscription__etudiant__nom', 'inscription__etudiant__prenom', 'montant', 'source', 'reference')  # Search across multiple fields
    readonly_fields = ('date_update', 'wave_launch_url', 'wave_id')  # Prevent modification of specific fields
    date_hierarchy = 'created'  # Allow filtering by creation date
    ordering = ('-created',)  # Order by creation date descending
    list_filter = ('inscription__etudiant__etablissement', 'active', 'confirmed')  # Filter by establishment, active/inactive, confirmed/unconfirmed
    resource_classes = [PaieResource]


    @method_decorator(cache_page(60*15))  # Cache cette page pour 15 minutes
    def changelist_view(self, request, extra_context=None):
        return super().changelist_view(request, extra_context)
    
    
 