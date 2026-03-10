from django.contrib import admin
from .models import Notification  # Assurez-vous que le chemin vers votre modèle est correct

# Register your models here.
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('titre', 'active', 'created', 'date_update')
    list_filter = ('active', 'created', 'date_update')
    search_fields = ('titre', 'description')
    readonly_fields = ('created', 'date_update')

# Notez que vous pouvez personnaliser les options d'affichage et de filtrage en fonction de vos besoins.
