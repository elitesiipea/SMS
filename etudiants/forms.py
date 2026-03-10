from django import forms
from .models import Etudiant, EtablissementDorigine,  SessionSoutenanceNew, SessionDiplome, Diplome, Certificat, CertificatSession
from django.contrib.auth.forms import PasswordChangeForm
from django_countries.widgets import CountrySelectWidget

class StudentPhotoForm(forms.ModelForm):
    class Meta:
        model = Etudiant
        fields = ['photo']


class EtudiantForm(forms.ModelForm):
    class Meta:
        model = Etudiant
        exclude = ['utilisateur','etablissement','active', 'created', 'date_update']

        widgets = {
            'nationalite': CountrySelectWidget(),
        }

    def __init__(self, *args, **kwargs):
        super(EtudiantForm, self).__init__(*args, **kwargs)
        
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

class PasswordChangeCustomForm(PasswordChangeForm):
    def __init__(self, user, *args, **kwargs):
        super(PasswordChangeCustomForm, self).__init__(user, *args, **kwargs)
        self.fields['old_password'].widget.attrs.update(
            {'class': 'form-control prompt srch_explore'})
        self.fields['new_password1'].widget.attrs.update(
            {'class': 'form-control prompt srch_explore'})
        self.fields['new_password2'].widget.attrs.update(
            {'class': 'form-control prompt srch_explore'})
        
        
        
        
        
class EtudiantUpdateForm(forms.ModelForm):
    class Meta:
        model = Etudiant
        exclude = [
            'utilisateur','type_etudiant','lieu_de_naissance',
            'nationalite','matricule','nom','prenom','etablissement',
            'active', 'created','date_update','photo','extrait','diplome',
            'fiche_orientation','piece','dictaticiel','sans_bac','active',
            'extrait_depose','piece_depose','photo_depose','diplome_depose',
            'fiche_orientation_depose','created','carte_etudiant',
            'date_update','code_paiement','photo_updated'
            ]
        
    def __init__(self, *args, **kwargs):
        super(EtudiantUpdateForm, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control required', 'style':'border: 2px solid black'})
        
class SessionSoutenanceNewForm(forms.ModelForm):
    class Meta:
        model = SessionSoutenanceNew
        fields = ['titre','fichier']
        
    def __init__(self, *args, **kwargs):
        super(SessionSoutenanceNewForm, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control required', 'style':'border: 2px solid black'})

    fichier = forms.FileField(label='Sélectionnez le fichier Excel')
        
        
from ajax_select.fields import AutoCompleteSelectMultipleField

class DocumentForm(forms.ModelForm):

    class Meta:
        model = EtablissementDorigine
        fields  = []

    tags = AutoCompleteSelectMultipleField('tags')
    
    
class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(label='Sélectionnez le fichier Excel', widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))



class SessionDiplomeNewForm(forms.ModelForm):
    class Meta:
        model = SessionDiplome
        fields = ['titre','fichier']
        
    def __init__(self, *args, **kwargs):
        super(SessionDiplomeNewForm, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control required', 'style':'border: 2px solid black'})

    fichier = forms.FileField(label='Sélectionnez le fichier Excel')

class SessionCertificatNewForm(forms.ModelForm):
    class Meta:
        model = CertificatSession
        fields = ['titre','fichier']
        
    def __init__(self, *args, **kwargs):
        super(SessionCertificatNewForm, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control required', 'style':'border: 2px solid black'})

    fichier = forms.FileField(label='Sélectionnez le fichier Excel')