from django import forms
from .models import CategorieProduit, Produit, Fournisseur, Commande, ProduitCommande
from django.forms import inlineformset_factory

class CategorieProduitForm(forms.ModelForm):
    class Meta:
        model = CategorieProduit
        fields = ['nom']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['nom', 'categorie', 'quantite', 'localisation', 'description', 'image']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'categorie': forms.Select(attrs={'class': 'form-control'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control'}),
            'localisation': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }
class FournisseurForm(forms.ModelForm):
    class Meta:
        model = Fournisseur
        fields = ['nom', 'email', 'contact', 'produits']
        widgets = {
            'produits': forms.CheckboxSelectMultiple(),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        etablissement = kwargs.pop('etablissement', None)
        super(FournisseurForm, self).__init__(*args, **kwargs)
        if etablissement:
            self.fields['produits'].queryset = CategorieProduit.objects.filter(etablissement=etablissement)
            
class CommandeForm(forms.ModelForm):
    class Meta:
        model = Commande
        fields = ['fournisseur',]
        widgets = {
            'fournisseur': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(CommandeForm, self).__init__(*args, **kwargs)
        if user and user.is_authenticated:
            self.fields['fournisseur'].queryset = Fournisseur.objects.filter(etablissement=user.etablissement)

class ProduitCommandeForm(forms.ModelForm):
    class Meta:
        model = ProduitCommande
        fields = ['produit', 'quantite']
        widgets = {
            'produit': forms.Select(attrs={'class': 'form-control'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control'}),
        }

ProduitCommandeFormSet = inlineformset_factory(
    Commande,
    ProduitCommande,
    form=ProduitCommandeForm,
    extra=5,
    can_delete=True
)


class MarkCommandeReceivedForm(forms.ModelForm):
    class Meta:
        model = Commande
        fields = ['bon_de_commande', 'commande_recu']
        widgets = {
            'bon_de_commande': forms.FileInput(attrs={'class': 'form-control'}),
            'commande_recu': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(MarkCommandeReceivedForm, self).__init__(*args, **kwargs)
        self.fields['commande_recu'].label = 'Marquer comme reçu'