from django.contrib import admin
from .models import CategorieLivre, Livre
# Register your models here.

class LivreInline(admin.TabularInline):
    model = Livre
    extra = 0

@admin.register(CategorieLivre)
class CategorieLivreInline(admin.ModelAdmin):
    search_fields = ['nom']
    inlines = [LivreInline,]
    list_display = ('nom','active', 'created', 'date_update')
    
@admin.register(Livre)
class LivreAdmin(admin.ModelAdmin):
    search_fields = ['titre']
    list_display = ('titre', 'categorie', 'auteur', 'active', 'created', 'date_update', )