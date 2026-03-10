from django.contrib import admin
from .models import Note, Resultat


class ResultatInline(admin.TabularInline):
    model = Resultat
    extra = 1  # Number of extra empty Resultat forms to display

class NoteAdmin(admin.ModelAdmin):
    # inlines = [ResultatInline]
    list_display = ('classe', 'matiere', 'coefficient_note_partiel','coeeficient_matiere','active', 'created', 'date_update')
    list_filter = ('active', 'created', 'date_update')
    search_fields = ['classe__filiere__nom','classe__niveau__nom', 'matiere__matiere__nom']
    # Add other options as needed

    def get_queryset(self, request):
        # Récupérer l'établissement de l'utilisateur connecté
        etablissement = request.user.etablissement
        # Filtrer les emplois du temps par établissement de l'utilisateur connecté
        queryset = Note.objects.filter(classe__annee_academique__etablissement=etablissement)
        return queryset

admin.site.register(Note, NoteAdmin)



class ResultatAdmin(admin.ModelAdmin):
    list_display = ('note', 'etudiant', 'note_1', 'note_2', 'note_3','note_partiel','moyenne', 'moyenne_coefficient','active', 'created', 'date_update')
    list_filter = ('active', 'created', 'date_update', 'session')
    search_fields = [
       'note__classe__niveau__nom',
       'note__classe__filiere__nom',
       'note__classe__nom',
       'etudiant__etudiant__nom',
       'etudiant__etudiant__prenom',
       'etudiant__etudiant__utilisateur__nom',
       'etudiant__etudiant__utilisateur__prenom',
       
    ]
    
    def get_queryset(self, request):
        # Récupérer l'établissement de l'utilisateur connecté
        etablissement = request.user.etablissement
        # Filtrer les emplois du temps par établissement de l'utilisateur connecté
        queryset = Resultat.objects.filter(note__classe__annee_academique__etablissement=etablissement)
        return queryset
    # Add other options as needed
    
admin.site.register(Resultat, ResultatAdmin)
