from django.contrib import admin
from .models import Resume, Information, Data

# Inline pour le modèle Information
class InformationInline(admin.TabularInline):
    model = Information
    extra = 0

# Inline pour le modèle Data
class DataInline(admin.TabularInline):
    model = Data
    extra = 0
# Admin pour le modèle Resume
@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    search_fields = ["etudiant__nom", "etudiant__prenom", "etudiant__etablissement__nom"]
    list_display = ("etudiant", "active", "created", "date_update")

    inlines = [InformationInline, DataInline]
    def get_queryset(self, request):
        # Récupérer l'établissement de l'utilisateur connecté
        etablissement = request.user.etablissement
        # Appeler la méthode personnalisée pour filtrer les utilisateurs
        queryset = Resume.objects.filter(etudiant__etablissement=etablissement)
        return queryset

# Admin pour le modèle Information
@admin.register(Information)
class InformationAdmin(admin.ModelAdmin):
    search_fields = ["resume__etudiant__nom", "resume__etudiant__prenom", "resume__etudiant__etablissement__nom"]
    list_display = ("resume", "nature", "intitule", "etablissement", "active", "created", "date_update")

    def get_queryset(self, request):
        # Récupérer l'établissement de l'utilisateur connecté
        etablissement = request.user.etablissement
        # Appeler la méthode personnalisée pour filtrer les utilisateurs
        queryset = Information.objects.filter(resume__etudiant__etablissement=etablissement)
        return queryset

# Admin pour le modèle Data
@admin.register(Data)
class DataAdmin(admin.ModelAdmin):
    search_fields = ["resume__etudiant__nom", "resume__etudiant__prenom", "resume__etudiant__etablissement__nom"]
    list_display = ("resume", "nature", "intitule", "active", "created", "date_update")

    def get_queryset(self, request):
        # Récupérer l'établissement de l'utilisateur connecté
        etablissement = request.user.etablissement
        # Appeler la méthode personnalisée pour filtrer les utilisateurs
        queryset = Data.objects.filter(resume__etudiant__etablissement=etablissement)
        return queryset
