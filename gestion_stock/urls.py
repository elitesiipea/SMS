from django.urls import path
from . import views

urlpatterns = [
    path('produits/', views.produit_view, name='produit_view'),
    path('categorie/delete/<int:pk>/', views.delete_category, name='delete_category'),
    path('produit/delete/<int:pk>/', views.delete_product, name='delete_product'),
    path('categorie/ajouter/', views.produit_view, name='add_category'),
    path('produit/ajouter/', views.produit_view, name='add_product'),
    
    path('categorie/edit/<int:pk>/', views.edit_category, name='edit_category'),
    path('produit/edit/<int:pk>/', views.edit_product, name='edit_product'),
    
    path('fournisseurs/', views.fournisseur_list, name='fournisseur_list'),
    path('fournisseurs/add/', views.add_fournisseur, name='add_fournisseur'),
    path('fournisseurs/edit/<int:pk>/', views.edit_fournisseur, name='edit_fournisseur'),
    path('fournisseurs/delete/<int:pk>/', views.delete_fournisseur, name='delete_fournisseur'),
    
    path('commandes/ajouter/', views.create_commande, name='create_commande'),
     
    path('commandes/', views.commande_list, name='commande_list'),
    path('commandes/edit/<int:pk>/', views.edit_commande, name='edit_commande'),
    path('commandes/mark_received/<int:pk>/', views.mark_commande_as_received, name='mark_commande_as_received'),
    path('commandes/delete/<int:pk>/', views.delete_commande, name='delete_commande'),
    path('commandes/print/<int:pk>/', views.print_commande, name='print_commande'),
    path('commande/<int:pk>/mark-received/', views.mark_commande_as_received, name='mark_commande_as_received'),
    
    path('produit/<int:produit_id>/historique/', views.produit_historique, name='produit_historique'),
]
