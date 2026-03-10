from django.contrib import admin
from .models import (User)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    search_fields = ["nom", "prenom", "etablissement__nom"]
    list_display = ("email", "nom", "prenom","etablissement", "is_student", "is_teacher", 
                    "is_staff", "is_active",  'can_register_student', 'can_register_teacher', 'can_update_fees')
    def get_queryset(self, request):
        # Récupérer l'établissement de l'utilisateur connecté
        etablissement = request.user.etablissement
        # Appeler la méthode personnalisée pour filtrer les utilisateurs
        queryset = User.objects.filter(etablissement=etablissement)
        return queryset


