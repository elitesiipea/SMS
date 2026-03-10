from django.contrib import admin
import secrets
import string
from .models import (Etablissement, 
                     Salle,
                     Filiere, 
                     Niveau,
                     AnneeAcademique, 
                     Classe, 
                     Maquette,
                     UniteEnseignement,
                     Matiere,
                     StudentMessage, 
                     Campus,
                     Student 
                     )

# Register your models here.

class FiliereInline(admin.TabularInline):

    model = Filiere
    extra = 0

class NiveauInline(admin.TabularInline):
    model = Niveau
    extra = 0


@admin.register(Etablissement)
class EtablissementAdmin(admin.ModelAdmin):
    search_fields = ['nom']
    list_display = ('nom','sigle','code','active', 'created', 'date_update')
    search_fields = ('nom',)
    inlines = [FiliereInline,NiveauInline,]



class SalleAdmin(admin.ModelAdmin):
    list_display = ('nom', 'capacite', 'active', 'created', 'date_update')
    list_filter = ('etablissement', 'active')
    search_fields = ('nom',)
    
    def get_queryset(self, request):
        # Récupérer l'établissement de l'utilisateur connecté
        etablissement = request.user.etablissement
        # Appeler la méthode personnalisée pour filtrer les utilisateurs
        queryset = Salle.objects.filter(etablissement=etablissement)
        return queryset

admin.site.register(Salle, SalleAdmin)

class CampusAdmin(admin.ModelAdmin):
    list_display = ('nom', 'active', 'created', 'date_update')
    list_filter = ('etablissement', 'active')
    search_fields = ('nom',)
    
    def get_queryset(self, request):
        # Récupérer l'établissement de l'utilisateur connecté
        etablissement = request.user.etablissement
        # Appeler la méthode personnalisée pour filtrer les utilisateurs
        queryset = Campus.objects.filter(etablissement=etablissement)
        return queryset

admin.site.register(Campus, CampusAdmin)

@admin.register(Filiere)
class FiliereAdmin(admin.ModelAdmin):
    list_display = ('etablissement', 'nom', 'sigle', 'active', 'created', 'date_update', )
    search_fields = ('etablissement__nom', 'nom', 'sigle', )

    def get_queryset(self, request):
        # Récupérer l'établissement de l'utilisateur connecté
        etablissement = request.user.etablissement
        # Appeler la méthode personnalisée pour filtrer les utilisateurs
        queryset = Filiere.objects.filter(etablissement=etablissement)
        return queryset



@admin.register(Niveau)
class NiveauiAdmin(admin.ModelAdmin):
    list_display = ('etablissement', 'nom', 'active', 'created', 'date_update', )
    search_fields = ('etablissement__nom', 'nom')

    def get_queryset(self, request):
        # Récupérer l'établissement de l'utilisateur connecté
        etablissement = request.user.etablissement
        # Appeler la méthode personnalisée pour filtrer les utilisateurs
        queryset = Niveau.objects.filter(etablissement=etablissement)
        return queryset

@admin.register(AnneeAcademique)
class AnneeAcademiqueAdmin(admin.ModelAdmin):
    list_display = ('etablissement', 'debut', 'fin', 'active', 'created', 'date_update', )
    search_fields = ('etablissement__nom','debut', 'fin',)

    def get_queryset(self, request):
        # Récupérer l'établissement de l'utilisateur connecté
        etablissement = request.user.etablissement
        # Appeler la méthode personnalisée pour filtrer les utilisateurs
        queryset = AnneeAcademique.objects.filter(etablissement=etablissement)
        return queryset


@admin.register(Classe)
class ClasseAdmin(admin.ModelAdmin):
    list_display = ('nom', 'annee_academique', 'filiere', 'niveau', 
                    'classe_universitaire', 'classe_professionnelle_jour', 
                    'classe_professionnelle_soir', 'classe_online',                     'active', 'created', 'date_update', )
    search_fields = ('nom', 'filiere__nom', 'niveau__nom',)

    def get_queryset(self, request):
        # Récupérer l'établissement de l'utilisateur connecté
        etablissement = request.user.etablissement
        # Appeler la méthode personnalisée pour filtrer les utilisateurs
        queryset = Classe.objects.filter(annee_academique__etablissement=etablissement)
        return queryset
    
    

from django.contrib import admin

class MatiereInline(admin.TabularInline):
    model = Matiere
    extra = 1  # Nombre de lignes vierges supplémentaires à ajouter
    # Si le nombre de matières est très important, vous pouvez ajouter des options de pagination ici.

class UniteEnseignementInline(admin.TabularInline):
    model = UniteEnseignement
    extra = 1  # Ajuster en fonction des besoins

@admin.register(Maquette)
class MaquetteAdmin(admin.ModelAdmin):
    list_display = (
        'etablissement', 'filiere', 'niveau', 'annee_academique', 'active', 
        'maquette_universitaire', 'maquette_professionnel_jour', 'maquette_professionnel_soir', 
        'maquette_cours_en_ligne', 'created', 'date_update',
    )
    search_fields = ('etablissement__nom', 'filiere__nom', 'niveau__nom',)
    list_filter = ('etablissement', 'filiere', 'niveau', 'annee_academique', 'active')
    list_per_page = 20  # Limite le nombre de résultats par page

    # Ajout des inlines de matières et unités d'enseignement
    inlines = [UniteEnseignementInline]

    def get_queryset(self, request):
        etablissement = request.user.etablissement
        # Optimisation des requêtes avec select_related pour minimiser les requêtes SQL
        queryset = Maquette.objects.filter(etablissement=etablissement).select_related(
            'etablissement', 'filiere', 'niveau', 'annee_academique'
        )
        return queryset



@admin.register(UniteEnseignement)
class UniteEnseignementAdmin(admin.ModelAdmin):
    list_display = ('maquette', 'nom', 'semestre', 'categorie', 'active', 'created', 'date_update', )
    search_fields = ('maquette__filiere__nom','maquette__niveau__nom','semestre', 'categorie',)

    def get_queryset(self, request):
        # Récupérer l'établissement de l'utilisateur connecté
        etablissement = request.user.etablissement
        # Appeler la méthode personnalisée pour filtrer les utilisateurs
        queryset = UniteEnseignement.objects.filter(maquette__etablissement=etablissement)
        return queryset

@admin.register(Matiere)
class MatiereAdmin(admin.ModelAdmin):
    list_display = (
        'unite', 
        'nom', 
        'coefficient', 
        'volume_horaire', 
        'taux_horaire', 
        'active', 
        'created', 
        'date_update', 
        'get_filiere',      # Add filiere to the list display
        'get_niveau',       # Add niveau to the list display
        'get_annee_academique',  # Add annee_academique to the list display
    )
    
    search_fields = (
        'unite__nom', 
        'nom', 
        'unite__maquette__filiere__nom', 
        'unite__maquette__niveau__nom', 
        'unite__semestre', 
        'unite__categorie',
        'unite__maquette__annee_academique__nom',  # Add annee_academique to the search fields
    )
    
    list_filter = (
        'unite__maquette__annee_academique',  # Filter by annee_academique
        'unite__maquette__filiere',           # Filter by filiere
        'unite__maquette__niveau',            # Filter by niveau
        'unite__semestre',                    # Filter by semestre
        'active',                             # Filter by active status
    )

    def get_queryset(self, request):
        # Récupérer l'établissement de l'utilisateur connecté
        etablissement = request.user.etablissement
        # Appeler la méthode personnalisée pour filtrer les utilisateurs
        queryset = super().get_queryset(request).filter(unite__maquette__etablissement=etablissement)
        return queryset
    
    # Define method to get filiere from the related Maquette
    def get_filiere(self, obj):
        return obj.unite.maquette.filiere
    get_filiere.short_description = 'Filière'  # Optional: Customize the column header in admin

    # Define method to get niveau from the related Maquette
    def get_niveau(self, obj):
        return obj.unite.maquette.niveau
    get_niveau.short_description = 'Niveau'  # Optional: Customize the column header in admin

    # Define method to get annee_academique from the related Maquette
    def get_annee_academique(self, obj):
        return obj.unite.maquette.annee_academique
    get_annee_academique.short_description = 'Année Académique'  # Optional: Customize the column header in admin

    

@admin.register(StudentMessage)
class StudentMessageAdmin(admin.ModelAdmin):
    list_display = ('titre', 'etablissement', 'active', 'created', 'date_update')
    list_filter = ('etablissement', 'active', 'created', 'date_update')
    search_fields = ('titre', 'etablissement__nom')  # Add any fields you want to search by

    def get_queryset(self, request):
        # Récupérer l'établissement de l'utilisateur connecté
        etablissement = request.user.etablissement
        # Appeler la méthode personnalisée pour filtrer les utilisateurs
        queryset = StudentMessage.objects.filter(etablissement=etablissement)
        return queryset


    

    # Customize other aspects of the admin page if needed
from django.contrib import admin
from .models import SessionDiplome, Diplome

@admin.register(SessionDiplome)
class SessionDiplomeAdmin(admin.ModelAdmin):
    list_display = ('titre', 'etablissement', 'active', 'created', 'date_update', 'candidats_nb')
    search_fields = ('titre', 'etablissement__nom')  # Assuming 'nom' is a field in Etablissement model
    list_filter = ('active', 'created', 'etablissement')
    date_hierarchy = 'created'
    ordering = ('-created',)
    readonly_fields = ('created', 'date_update', 'candidats_nb')

    def candidats_nb(self, obj):
        return obj.candidats_nb
    candidats_nb.short_description = 'Nombre de Candidats'
    
    def get_queryset(self, request):
        # Récupérer l'établissement de l'utilisateur connecté
        etablissement = request.user.etablissement
        # Appeler la méthode personnalisée pour filtrer les utilisateurs
        queryset = SessionDiplome.objects.filter(etablissement=etablissement)
        return queryset


@admin.register(Diplome)
class DiplomeAdmin(admin.ModelAdmin):
    list_display = ('matricule', 'nom', 'prenom', 'diplome', 'niveau', 'cycle', 'session', 'code')
    search_fields = ('matricule', 'nom', 'prenom', 'diplome', 'session__titre')
    list_filter = ('niveau', 'cycle', 'annee_academique', 'session')
    ordering = ('nom', 'prenom')
    readonly_fields = ('code',)
    fieldsets = (
        (None, {
            'fields': ('session', 'matricule', 'nom', 'prenom', 'date_de_naissance', 'lieu_de_naissance', 'contact1', 'contact2', 'diplome', 'niveau', 'annee_academique', 'date_soutenance', 'session_soutenance', 'cycle')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('code',),
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.code:
            chars = (string.ascii_uppercase + string.digits).upper()
            obj.code = ''.join(secrets.choice(chars) for _ in range(12))
            while Diplome.objects.filter(code=obj.code).exists():
                obj.code = ''.join(secrets.choice(chars) for _ in range(12))
        super().save_model(request, obj, form, change)
        
    def get_queryset(self, request):
        # Récupérer l'établissement de l'utilisateur connecté
        etablissement = request.user.etablissement
        # Appeler la méthode personnalisée pour filtrer les utilisateurs
        queryset = Diplome.objects.filter(session__etablissement=etablissement)
        return queryset


from django.contrib import admin
from .models import ClasseProgression, Pointage

from django.contrib import admin
from .models import ClasseProgression, Pointage

class PointageInline(admin.TabularInline):  
    """Affichage des pointages sous forme d'inline dans ClasseProgression"""
    model = Pointage
    extra = 1  # Nombre de champs vides à afficher
    fields = ('volume_realise', 'observation', 'created', 'active')
    readonly_fields = ('created', 'date_update')
    can_delete = True

@admin.register(ClasseProgression)
class ClasseProgressionAdmin(admin.ModelAdmin):
    list_display = ('classe', 'matiere', 'enseignant', 'volume_realise', 'progress', 'is_close', 'is_locked', 'created')
    list_filter = ('active', 'cours_en_tronc_commun', 'note_deposee', 'paiement_effectue', 'demande_de_paiement_initie', 'matiere', 'enseignant')
    search_fields = ('classe__nom', 'matiere__nom', 'enseignant')
    date_hierarchy = 'created'
    ordering = ('-created',)
    inlines = [PointageInline]

@admin.register(Pointage)
class PointageAdmin(admin.ModelAdmin):
    list_display = ('matiere', 'volume_realise', 'created', 'active')
    list_filter = ('active', 'created')
    search_fields = ('matiere__classe__nom', 'matiere__matiere__nom', 'volume_realise', 'observation')
    date_hierarchy = 'created'
    ordering = ('-created',)

    
    # Additional configurations can be added as needed.


from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'ident_perm', 'filiere', 'niveau', 'classe', 'status', 'sexe', 'contact', 'email',)
    list_filter = ('filiere', 'niveau', 'classe', 'status', 'sexe', 'etablissement')
    search_fields = ('nom', 'prenom', 'ident_perm', 'email', 'contact')
    ordering = ('nom',)
    readonly_fields = ('code_unique', 'email')
    fieldsets = (
        ("Informations personnelles", {
            'fields': ('ident_perm', 'nom', 'prenom', 'date_naissance', 'lieu_naissance', 'sexe', 'contact', 'photo')
        }),
        ("Détails académiques", {
            'fields': ('filiere', 'niveau', 'classe', 'elite_id', 'status', 'etablissement')
        }),
        ("Informations système", {
            'fields': ('code_unique', 'email', )
        }),
    )
    list_per_page = 100