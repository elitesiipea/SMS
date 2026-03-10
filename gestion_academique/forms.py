from django import forms
from .models import Maquette, UniteEnseignement, Matiere, Classe

class SelectClassesForm(forms.Form):
    classes = forms.ModelMultipleChoiceField(queryset=Classe.objects.all(), widget=forms.CheckboxSelectMultiple)


class MaquetteForm(forms.ModelForm):
    class Meta:
        model = Maquette
        exclude = ['created', 'etablissement', 'date_update']

    def __init__(self, etablissement_id, *args, **kwargs):
        super(MaquetteForm, self).__init__(*args, **kwargs)
        self.fields['filiere'].queryset = self.fields['filiere'].queryset.filter(etablissement_id=etablissement_id)
        self.fields['niveau'].queryset = self.fields['niveau'].queryset.filter(etablissement_id=etablissement_id)
        self.fields['annee_academique'].queryset = self.fields['annee_academique'].queryset.filter(etablissement_id=etablissement_id)

        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control required'})

class UniteEnseignementForm(forms.ModelForm):
    class Meta:
        model = UniteEnseignement
        exclude = ['maquette', 'active', 'created', 'date_update']

    def __init__(self, *args, **kwargs):
        super(UniteEnseignementForm, self).__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control required', 'style': 'border: 2px solid'})


class MatiereForm(forms.ModelForm):
    class Meta:
        model = Matiere
        exclude = ['maquette', 'active', 'created', 'date_update']

    def __init__(self, maquette_id, *args, **kwargs):
        super(MatiereForm, self).__init__(*args, **kwargs)
        self.fields['unite'].queryset = UniteEnseignement.objects.filter(maquette=Maquette.objects.get(pk=maquette_id))

        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control required', 'style': 'border: 2px solid'})


from django import forms
from .models import SessionDiplome

class SessionDiplomeForm(forms.ModelForm):
    class Meta:
        model = SessionDiplome
        fields = ['titre']
        
    def __init__(self, *args, **kwargs):
        super(SessionDiplomeForm, self).__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control required', 'style': 'border: 2px solid'})

class UploadFileForm(forms.Form):
    file = forms.FileField()