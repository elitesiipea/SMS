from django.contrib import admin
from .models import (
    CategorieProduit, Produit, Fournisseur, Commande, ProduitCommande, 
    Operation, ProduitOperation
)

# ---- Inlines ----

class ProduitInline(admin.TabularInline):
    model = Produit
    extra = 1  # Defines how many empty inline forms are displayed
    fields = ['nom', 'quantite', 'quantite_minimal', 'localisation', 'description']
    readonly_fields = ['quantite']  # Optionally, you can set this to prevent editing

class ProduitCommandeInline(admin.TabularInline):
    model = ProduitCommande
    extra = 1
    fields = ['produit', 'quantite']
    autocomplete_fields = ['produit']  # Enables autocomplete for related products

class ProduitOperationInline(admin.TabularInline):
    model = ProduitOperation
    extra = 1
    fields = ['produit', 'quantite']

# ---- Admin Classes ----

@admin.register(CategorieProduit)
class CategorieProduitAdmin(admin.ModelAdmin):
    list_display = ['nom', 'active', 'created', 'date_update']
    search_fields = ['nom']
    list_filter = ['active', 'created', 'date_update']

    def get_queryset(self, request):
        etablissement = request.user.etablissement
        queryset = super().get_queryset(request)
        return queryset.filter(etablissement=etablissement)

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ['nom', 'categorie', 'quantite', 'quantite_minimal', 'localisation', 'active', 'created']
    search_fields = ['nom', 'categorie__nom']
    list_filter = ['categorie', 'active', 'created']
    autocomplete_fields = ['categorie']

    def get_queryset(self, request):
        etablissement = request.user.etablissement
        queryset = super().get_queryset(request)
        return queryset.filter(categorie__etablissement=etablissement)

@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ['nom', 'email', 'contact', 'active', 'created']
    search_fields = ['nom', 'email', 'contact']
    list_filter = ['active', 'created']
   

    def get_queryset(self, request):
        etablissement = request.user.etablissement
        queryset = super().get_queryset(request)
        return queryset.filter(etablissement=etablissement)

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ['fournisseur', 'commande_recu', 'active', 'created']
    search_fields = ['fournisseur__nom']
    list_filter = ['commande_recu', 'active', 'created']
    

    def get_queryset(self, request):
        etablissement = request.user.etablissement
        queryset = super().get_queryset(request)
        return queryset.filter(fournisseur__etablissement=etablissement)

@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = ['type', 'reference', 'returned', 'active', 'created']
    search_fields = ['type', 'reference']
    list_filter = ['type', 'returned', 'active', 'created']
    inlines = [ProduitOperationInline]

    def get_queryset(self, request):
        etablissement = request.user.etablissement
        queryset = super().get_queryset(request)
        return queryset.filter(etablissement=etablissement)

@admin.register(ProduitOperation)
class ProduitOperationAdmin(admin.ModelAdmin):
    list_display = ['operation', 'produit', 'quantite', 'active', 'created']
    search_fields = ['operation__reference', 'produit__nom']
    list_filter = ['active', 'created']

    def get_queryset(self, request):
        etablissement = request.user.etablissement
        queryset = super().get_queryset(request)
        return queryset.filter(operation__etablissement=etablissement)

@admin.register(ProduitCommande)
class ProduitCommandeAdmin(admin.ModelAdmin):
    list_display = ['commande', 'produit', 'quantite', 'active', 'created']
    search_fields = ['commande__fournisseur__nom', 'produit__nom']
    list_filter = ['active', 'created']

    def get_queryset(self, request):
        etablissement = request.user.etablissement
        queryset = super().get_queryset(request)
        return queryset.filter(commande__fournisseur__etablissement=etablissement)
