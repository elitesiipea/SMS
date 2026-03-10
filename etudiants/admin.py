from django.contrib import admin
from .models import Etudiant, EtablissementDorigine, AttestationNew, SessionSoutenanceNew, Diplome, SessionDiplome, Certificat, CertificatSession
from import_export.admin import ImportExportModelAdmin
# Register your models here.


class DiplomeAdmin(admin.ModelAdmin):
    list_display = ['nom', 'prenom', 'diplome', 'date_de_naissance', 'lieu_de_naissance', 'cycle', 'niveau', 'annee_academique', 'session', 'active', 'code']
    list_filter = ['diplome', 'cycle', 'niveau', 'annee_academique', 'session', 'active']
    search_fields = ['nom', 'prenom', 'lieu_de_naissance', 'code']
    readonly_fields = ['code']
    fieldsets = [
        ('Informations personnelles', {'fields': ['nom', 'prenom', 'date_de_naissance', 'lieu_de_naissance']}),
        ('Diplôme', {'fields': ['diplome', 'cycle', 'niveau', 'annee_academique', 'session']}),
        ('Statut', {'fields': ['active']}),
        ('Code', {'fields': ['code'], 'classes': ['collapse']}),
    ]
    actions = ['make_inactive']

    def make_inactive(self, request, queryset):
        queryset.update(active=False)
    make_inactive.short_description = "Marquer comme inactif"

admin.site.register(Diplome, DiplomeAdmin)


@admin.register(EtablissementDorigine)
class EtablissementDorigineAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ('code', 'nom', 'dren', 'type_etablissement', 'statut', )
    search_fields = ('code', 'nom', 'dren', 'type_etablissement', 'statut',)


@admin.register(Etudiant)
class EtudiantAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'type_etudiant', 'etablissement', 'etablissement_d_origine', 
                    'date_de_naissance', 'lieu_de_naissance', 'matricule_mers', 'numero_table_bac', 
                   'matricule', 'matricule', 'lieu_de_residence', 'sexe',
                    'serie_bac', 'contact', 'contactparent', 'code_paiement',
                    )
    search_fields = ('utilisateur__nom','utilisateur__prenom','code_paiement')
    autocomplete_fields = ['etablissement_d_origine']

    def get_queryset(self, request):
        # Récupérer l'établissement de l'utilisateur connecté
        etablissement = request.user.etablissement
        # Filtrer les emplois du temps par établissement de l'utilisateur connecté
        queryset = Etudiant.objects.filter(etablissement=etablissement)
        return queryset
    
    
class AttestationNewAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'matricule', 'date_de_naissance', 'lieu_de_naissance', 'pays', 'filiere', 'cycle', 'annee_academique', 'active', 'created', 'carte_etudiant', 'date_update')
    list_filter = ('pays', 'filiere', 'cycle', 'annee_academique', 'active', 'carte_etudiant')
    search_fields = ('nom', 'prenom', 'matricule', 'lieu_de_naissance')
    date_hierarchy = 'created'  # Ajoute une hiérarchie de dates
    ordering = ['nom', '-created']  # Tri par nom ascendant et date de création descendant
    list_editable = ['active', 'carte_etudiant']  # Permet l'édition directe de ces champs dans la liste
    list_per_page = 20  # Nombre d'éléments par page dans la liste
    actions_on_top = True  # Affiche les actions en haut de la liste
    actions_on_bottom = True  # Affiche les actions en bas de la liste
    save_on_top = True  # Affiche les boutons de sauvegarde en haut de la page d'édition

admin.site.register(AttestationNew, AttestationNewAdmin)

admin.site.register(SessionDiplome)


class SessionSoutenanceNewAdmin(admin.ModelAdmin):
    list_display = ('titre', 'etablissement', 'fichier', 'active', 'created', 'carte_etudiant', 'date_update', 'code')
    list_filter = ('etablissement', 'active', 'carte_etudiant')
    search_fields = ('titre', 'code')

admin.site.register(SessionSoutenanceNew, SessionSoutenanceNewAdmin)

admin.site.register(Certificat)

admin.site.register(CertificatSession)
