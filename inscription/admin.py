from django.contrib import admin
from .models import Inscription, Paiement
from gestion_academique.models import Classe, Filiere, Niveau
# Register the Inscription model

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


# Register the Paiement model

@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ('inscription', 'montant', 'source', 'reference', 'active', 'created', 'date_update')
    list_filter = ('active', 'created', 'date_update')
    search_fields = ('inscription__etudiant__nom', 'inscription__etudiant__prenom', 'inscription__etudiant__matricule')
    # readonly_fields = ('inscription', 'montant', 'source', 'reference', 'active', 'created', 'date_update')
    
    def get_queryset(self, request):
        # Récupérer l'établissement de l'utilisateur connecté
        etablissement = request.user.etablissement
        # Appeler la méthode personnalisée pour filtrer les utilisateurs
        queryset = Paiement.objects.filter(inscription__etudiant__etablissement=etablissement)
        return queryset