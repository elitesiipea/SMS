from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import CategorieProduit, Produit, Fournisseur, Commande, ProduitCommande
from .forms import CategorieProduitForm, ProduitForm, FournisseurForm, CommandeForm, ProduitCommandeFormSet, MarkCommandeReceivedForm
from decorators.decorators import staff_required ,student_required
from django.contrib.auth.decorators import login_required

from django.urls import reverse_lazy

@login_required
@staff_required
def produit_view(request):
    categories = CategorieProduit.objects.filter(etablissement=request.user.etablissement)
    produits = Produit.objects.filter(categorie__etablissement=request.user.etablissement)

    if request.method == 'POST':
        if 'nom_produit' in request.POST:  # Ajout ou édition
            

            if request.POST.get('produit_id'): 
                    print(request.POST.get('categorie'))# Edition produit
                    produit = get_object_or_404(Produit, id=request.POST.get('produit_id'))
                    form = ProduitForm(request.POST, request.FILES, instance=produit)
                    if form.is_valid():
                        form.save()
                        messages.success(request, 'Produit mis à jour avec succès.')
            else:
                print('alerte 3')# Ajout produit
                form = ProduitForm(request.POST, request.FILES)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Produit ajouté avec succès.')
        else:
            
            # Ajout ou édition catégorie
            if request.POST.get('categorie_id'):  # Edition catégorie
                categorie = get_object_or_404(CategorieProduit, id=request.POST.get('categorie_id'))
                form = CategorieProduitForm(request.POST, instance=categorie)
                form.save()
                messages.success(request, 'Catégorie mise à jour avec succès.')
            else:  # Ajout catégorie
                
                form = CategorieProduitForm(request.POST)
                categorie = form.save(commit=False)
                categorie.etablissement = request.user.etablissement
                categorie.save()
                messages.success(request, 'Catégorie ajoutée avec succès.')

    return render(request, 'gestion_stock/produit.html', {
        'categories': categories,
        'produits': produits, 
        "titre" : f"Produit & Catégorie Produit du Stock",
        "info": "Produit & Catégorie Produit du Stock",
        "info2" : "Produit & Catégorie Produit du Stock",
        "datatable": True,
       
    })

@login_required
@staff_required
def delete_category(request, pk):
    categorie = get_object_or_404(CategorieProduit, id=pk)
    categorie.delete()
    messages.success(request, 'Catégorie supprimée avec succès.')
    return redirect('produit_view')

@login_required
@staff_required
def delete_product(request, pk):
    produit = get_object_or_404(Produit, id=pk)
    produit.delete()
    messages.success(request, 'Produit supprimé avec succès.')
    return redirect('produit_view')

@login_required
@staff_required
def edit_category(request, pk):
    categorie = get_object_or_404(CategorieProduit, id=pk)

    if request.method == 'POST':
        form = CategorieProduitForm(request.POST, instance=categorie)
        if form.is_valid():
            form.save()
            messages.success(request, 'Catégorie mise à jour avec succès.')
            return redirect('produit_view')  # Redirection après l'édition
    else:
        form = CategorieProduitForm(instance=categorie)

    return render(request, 'gestion_stock/edit_category.html', {'form': form, 'categorie': categorie})


@login_required
@staff_required
def edit_product(request, pk):
    produit = get_object_or_404(Produit, id=pk)

    if request.method == 'POST':
        form = ProduitForm(request.POST, request.FILES, instance=produit)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produit mis à jour avec succès.')
            return redirect('produit_view')  # Redirection après l'édition
    else:
        form = ProduitForm(instance=produit)

    return render(request, 'gestion_stock/edit_product.html', {'form': form, 'produit': produit})


@login_required
@staff_required  # Assurez-vous que vous avez ce décorateur défini
def fournisseur_list(request):
    fournisseurs = Fournisseur.objects.all()
    form = FournisseurForm(etablissement=request.user.etablissement)  # Assurez-vous que l'utilisateur a un établissement
    return render(request, 'gestion_stock/fournisseurs/fournisseur_list.html', 
        {
            'fournisseurs': fournisseurs, 
            'form': form, 
            "titre": "Liste des Fournisseurs",
            "info": "Fournisseurs",
            "info2": "Liste des Fournisseurs",
            "datatable": True,
        }
    )

@login_required
@staff_required
def add_fournisseur(request):
    if request.method == 'POST':
        form = FournisseurForm(request.POST)
        if form.is_valid():
            fournisseur = form.save(commit=False)
            fournisseur.etablissement = request.user.etablissement  # Assurez-vous que votre utilisateur a un établissement
            fournisseur.save()  # Sauvegarder le fournisseur
            form.save_m2m()  # Enregistrer les relations ManyToMany (produits)
            return redirect('fournisseur_list')
    else:
        form = FournisseurForm(etablissement=request.user.etablissement)
    return render(request, 'gestion_stock/fournisseurs/fournisseur_list.html', {'form': form})

@login_required
@staff_required
def edit_fournisseur(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    if request.method == 'POST':
        form = FournisseurForm(request.POST, instance=fournisseur)
        if form.is_valid():
            form.save()
            return redirect('fournisseur_list')
    else:
        form = FournisseurForm(instance=fournisseur)
    return render(request, 'gestion_stock/fournisseurs/fournisseur_edit.html', {'form': form, 'fournisseur_id': pk, 
                                                                                "titre": "Liste des Fournisseurs",
            "info": f"Modifier le fournisseur  {fournisseur}",
            "info2": f"Modifier le fournisseur {fournisseur}",
            })

@login_required
@staff_required
def delete_fournisseur(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    fournisseur.delete()
    return redirect('fournisseur_list')



@login_required
@staff_required  # Ensures that only staff can access this view
def create_commande(request):
    if request.method == 'POST':
        form = CommandeForm(request.POST, user=request.user)
        formset = ProduitCommandeFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            commande = form.save()
            produits = formset.save(commit=False)
            for produit in produits:
                produit.commande = commande
                produit.save()
            return redirect('commande_list')  # Redirect to the list of commandes
    else:
        form = CommandeForm(user=request.user)  # Pass the user to the form
        formset = ProduitCommandeFormSet()

    return render(request, 'gestion_stock/commandes/create_commande.html', {
        'form': form,
        'formset': formset,
         "titre": "Nouvelle Commande",
            "info": "Nouvelle Commande",
            "info2": "Commande",
            "datatable": False,
    })
    
    
@login_required
@staff_required  # Ensures that only staff can access this view
def commande_list(request):
    commandes = Commande.objects.filter(fournisseur__etablissement=request.user.etablissement)
    return render(request, 'gestion_stock/commandes/commande_list.html', {'commandes': commandes, 
            "titre": "Commandes",
            "info": "Liste des Commandes",
            "info2": "Commande",
            "datatable": True,})


@login_required
@staff_required
def edit_commande(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    
    if request.method == 'POST':
        form = CommandeForm(request.POST, request.FILES, instance=commande, user=request.user)
        formset = ProduitCommandeFormSet(request.POST, instance=commande)
        form.save()
        produits = formset.save(commit=False)
            # Loop through and assign the commande and save products
        for produit in produits:
                produit.commande = commande
                produit.save()

            # Handle deletion of products if needed
        for produit in formset.deleted_objects:
                produit.delete()

        return redirect('commande_list')  # Redirect to the list of commandes

    else:
        # Pre-fill the form and formset with existing data
        form = CommandeForm(instance=commande, user=request.user)
        formset = ProduitCommandeFormSet(instance=commande)

    return render(request, 'gestion_stock/commandes/edit_commande.html', {
        'form': form,
        'formset': formset,
        'commande': commande,
        "titre": "Éditer la Commande",
        "info": "Éditer la Commande",
        "info2": "Commande",
        "datatable": False,
    })

@login_required
def mark_commande_as_received(request, pk):
    # Get the specific commande
    commande = get_object_or_404(Commande, pk=pk)
    
    if request.method == 'POST':
        form = MarkCommandeReceivedForm(request.POST, request.FILES, instance=commande)
        
        if form.is_valid():
            # Mark as received and save the bon de commande
            commande.commande_recu = True
            form.save()

            # If marked as received, update the product stock quantities
            produits_commandes = ProduitCommande.objects.filter(commande=commande)
            for produit_commande in produits_commandes:
                    produit = produit_commande.produit
                    produit.quantite += produit_commande.quantite  # Update stock
                    produit.save()

            return redirect('commande_list')  # Redirect to the commandes list
    else:
        form = MarkCommandeReceivedForm(instance=commande)

    return render(request, 'gestion_stock/commandes/mark_commande_received.html', {
        'form': form,
        'commande': commande, 
        "titre": "Commandes",
            "info": "Mise à Jour  de la commande",
            "info2": "Commande",
            "datatable": True,}
    )

@login_required
@staff_required 
def delete_commande(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    commande.delete()
    return redirect('commande_list')

@login_required
@staff_required 
def print_commande(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    return render(request, 'gestion_stock/commandes/print_commande.html', {'commande': commande,  "titre": "Commandes",
            "info": "Impression",
            "info2": "Commande",
            "datatable": True,
            })
    
@login_required
@staff_required
def produit_historique(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    produit_commandes = ProduitCommande.objects.filter(produit=produit, commande__commande_recu=True)

    context = {
        'produit': produit,
        'produit_commandes': produit_commandes,
        'titre': f"Historique des commandes pour {produit.nom}",
        'info': f"Historique de {produit.nom}",
         "datatable": True,
    }
    return render(request, 'gestion_stock/produits/produit_historique.html', context)
