from django import forms
from .models import Enseignant, ContratEnseignant
from gestion_academique.models import Matiere, AnneeAcademique, Classe, Filiere, Niveau
from django.forms.widgets import CheckboxSelectMultiple
from django.contrib.auth.forms import PasswordChangeForm

class EnseignantForm(forms.ModelForm):
    class Meta:
        model = Enseignant
        exclude = ['utilisateur', 'etablissement','created', 'date_update', 'code',]

       

    def __init__(self, *args, **kwargs):
        super(EnseignantForm, self).__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control required'})

        for field_name, field in self.fields.items():
            if field_name == "date_de_naissance":
                field.widget.attrs.update({
                                            'class': 'form-control datepicker-here required',
                                            'id':"default-date",
                                            "placeholder":"dd/mm/yyyy",
                                            "aria-describedby":"basic-addon2",
                                            })




class ContratEnseignantForm(forms.ModelForm):
    class Meta:
        model = ContratEnseignant
        fields = ['annee_academique', 'filiere', 'niveau', 'matiere', 'classe', 'volume_horaire', 'taux_horaire', 'support', 'syllabus','support_depose', 'syllabus_depose',]

    def __init__(self,id,  *args, **kwargs):
        super(ContratEnseignantForm, self).__init__(*args, **kwargs)
        self.fields['annee_academique'].queryset  = AnneeAcademique.objects.filter(etablissement_id=id)
        self.fields['filiere'].queryset  = Filiere.objects.filter(etablissement_id=id)
        self.fields['niveau'].queryset  = Niveau.objects.filter(etablissement_id=id)
        self.fields['classe'].queryset  = Classe.objects.filter(annee_academique__etablissement_id=id)
        self.fields['matiere'].queryset  = Matiere.objects.filter(maquette__etablissement_id=id)

        # Add additional attributes to form fields, e.g., CSS classes
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control required'})
        
        

class PasswordChangeCustomForm(PasswordChangeForm):
    def __init__(self, user, *args, **kwargs):
        super(PasswordChangeCustomForm, self).__init__(user, *args, **kwargs)
        self.fields['old_password'].widget.attrs.update(
            {'class': 'form-control prompt srch_explore'})
        self.fields['new_password1'].widget.attrs.update(
            {'class': 'form-control prompt srch_explore'})
        self.fields['new_password2'].widget.attrs.update(
            {'class': 'form-control prompt srch_explore'})
        
        
# forms.py
from django import forms
from .models import Rib

class RibForm(forms.ModelForm):
    class Meta:
        model = Rib
        fields = ['banque', 'document']

    def __init__(self, *args, **kwargs):
        super(RibForm, self).__init__(*args, **kwargs)
        # Customize form widget attributes if needed
        self.fields['banque'].widget.attrs['class'] = 'form-control'
        self.fields['document'].widget.attrs['class'] = 'form-control-file'
