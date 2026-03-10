from django import forms
from .models import Inscription
from gestion_academique.models import Filiere, Niveau


class InscriptionForm(forms.ModelForm):
    class Meta:
        model = Inscription
        fields = ['nature','filiere', 'niveau','parcour','frais',
                  'code_parrain',
                  'piece',
                  'extrait',
                  'bac',
                  'fiche_orientation',
                  'photo',
                  'polo',
                  'macaron',
                  'cravate',
                  'tissu',
                  'rame',
                  'marqueur',
                  'passe_le_bts']

    def __init__(self,etablissement_id, *args, **kwargs):
        super(InscriptionForm, self).__init__(*args, **kwargs)

        self.fields['filiere'].queryset = Filiere.objects.filter(etablissement_id=etablissement_id).order_by('nom')

        self.fields['niveau'].queryset = Niveau.objects.filter(etablissement_id=etablissement_id).order_by('nom')

        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control required'})
            
            
# inscription/forms.py
from django import forms
from .models import Paiement

class PaiementForm2(forms.ModelForm):
    class Meta:
        model = Paiement
        fields = ['reference', 'montant', 'source', 'effectue_par',]
       