from django.contrib import admin
from .models import Note, Resultat

class ResultatAdmin(admin.ModelAdmin):
    list_display = ('note', 'etudiant', 'note_1', 'note_2', 'note_3', 'note_partiel', 'moyenne_calculee', 'moyenne_coefficient_calculee', 'active', 'created', 'date_update')
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
    list_per_page = 50
    raw_id_fields = ('note', 'etudiant')

    def get_queryset(self, request):
        etablissement = request.user.etablissement
        return Resultat.objects.filter(
            note__classe__annee_academique__etablissement=etablissement
        ).select_related('note', 'etudiant').prefetch_related('note__matiere', 'note__classe')

admin.site.register(Resultat, ResultatAdmin)


class NoteAdmin(admin.ModelAdmin):
    list_display = ('classe', 'matiere', 'coefficient_note_partiel', 'coeeficient_matiere', 'active', 'created', 'date_update')
    list_filter = ('active', 'created', 'date_update')
    search_fields = ['classe__filiere__nom', 'classe__niveau__nom', 'matiere__matiere__nom']
    list_per_page = 50
    raw_id_fields = ('classe', 'matiere')

    def get_queryset(self, request):
        etablissement = request.user.etablissement
        return Note.objects.filter(classe__annee_academique__etablissement=etablissement).select_related('classe', 'matiere')

admin.site.register(Note, NoteAdmin)
