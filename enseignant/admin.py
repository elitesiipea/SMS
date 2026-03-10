from django.contrib import admin
from .models import Enseignant, ContratEnseignant, TravauxDirige, Rib


class TdInline(admin.TabularInline):

    model = TravauxDirige
    extra = 0
    
class RibInline(admin.TabularInline):

    model = Rib
    extra = 0
    
    
@admin.register(Enseignant)
class EnseignantAdmin(admin.ModelAdmin):
    list_display = ['nom', 'prenom', 'email', 'etablissement', 'statut_enseignant']
    list_filter = ['etablissement', 'statut_enseignant', 'sexe']
    search_fields = ['nom', 'prenom', 'email', 'numero_cni', 'code']
    readonly_fields = ['code']
    inlines = [RibInline,]

    def get_queryset(self, request):
        # Récupérer l'établissement de l'utilisateur connecté
        etablissement = request.user.etablissement
        # Filtrer les emplois du temps par établissement de l'utilisateur connecté
        queryset = Enseignant.objects.filter(etablissement=etablissement)
        return queryset
    

@admin.register(TravauxDirige)
class EnseignantAdmin(admin.ModelAdmin):
    list_display = ['contrat', 'volume_horaire', 'taux_horaire', 'progression', 'paye']
    list_filter = ['contrat', 'volume_horaire', 'taux_horaire','progression','paye']
    search_fields = ['contrat__annee_academique__debut', 'contrat__annee_academique__fin', 
                     'contrat__enseignant__nom','contrat__enseignant__prenom', 
                     'contrat__filiere__nom', 'contrat__niveau__nom', 'contrat__matiere__nom']

@admin.register(ContratEnseignant)
class ContratEnseignantAdmin(admin.ModelAdmin):
    list_display = ['annee_academique', 'enseignant','classe', 'filiere', 'niveau', 'matiere', 'volume_horaire', 'progression', 'taux_horaire', 'closed','created']
    list_filter = ['annee_academique', 'enseignant', 'filiere', 'niveau']
    search_fields = ['annee_academique__debut', 'annee_academique__fin', 'enseignant__nom','enseignant__prenom', 'filiere__nom', 'niveau__nom', 'matiere__nom']
    list_per_page = 25
    inlines = [TdInline,]

    # Optionally, you can customize the display in the change form
    fieldsets = (
        ('Informations générales', {
            'fields': ('annee_academique', 'enseignant', 'filiere', 'niveau', 'matiere', 'classe','description')
        }),
        ('Contrat details', {
            'fields': ('volume_horaire','taux_horaire','progression')
        }),
        ('Cloudinary Fields', {
            'fields': ('support', 'syllabus')
        }),
        ('Support & Documents', {
            'fields': ('support_depose', 'syllabus_depose', 'cahier_de_texte', 'notes','closed' )
        }),

         ('Traitements', {
            'fields': ('demande_accompte', 'demande_traitee', 'numero_cheque','cheque_retire')
        }),

        
        
    )

    def get_queryset(self, request):
        # Récupérer l'établissement de l'utilisateur connecté
        etablissement = request.user.etablissement
        # Filtrer les emplois du temps par établissement de l'utilisateur connecté
        queryset = ContratEnseignant.objects.filter(enseignant__etablissement=etablissement)
        return queryset
    