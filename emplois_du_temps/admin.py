from django.contrib import admin
from .models import EmploisDutemps, Programme

class ProgrammeInline(admin.TabularInline):
    model = Programme
    extra = 0

@admin.register(EmploisDutemps)
class EmploisDutempsAdmin(admin.ModelAdmin):
    list_display = ('classe','active', 'created', 'date_update')
    list_filter = ('classe', 'active')
    search_fields = ('classe__nom', 'classe__annee_academique__debut','classe__annee_academique__fin')
    inlines = [ProgrammeInline,]

    def get_queryset(self, request):
        # Récupérer l'établissement de l'utilisateur connecté
        etablissement = request.user.etablissement
        # Filtrer les emplois du temps par établissement de l'utilisateur connecté
        queryset = EmploisDutemps.objects.filter(classe__annee_academique__etablissement=etablissement)
        return queryset

    


class ProgrammeAdmin(admin.ModelAdmin):
    list_display = ('emplois_du_temps', 'date', 'matiere', 'salle', 'jour', 'debut', 'fin', 'active', 'created', 'date_update')
    list_filter = ('jour', 'active')
    search_fields = ('salle__nom',)  # Assuming 'nom' is the field you want to search on the related 'Salle' model
    
    def get_queryset(self, request):
        # Récupérer l'établissement de l'utilisateur connecté
        etablissement = request.user.etablissement
        # Filtrer les emplois du temps par établissement de l'utilisateur connecté
        queryset = Programme.objects.filter(emplois_du_temps__classe__annee_academique__etablissement=etablissement)
        return queryset

admin.site.register(Programme, ProgrammeAdmin)