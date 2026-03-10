from django import forms
from .models import Maquette, UniteEnseignement, Matiere, Classe, Filiere, Filiere, Niveau, AnneeAcademique, \
    Etablissement


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
    
    
# forms.py
from django import forms
from .models import ClasseProgression, Pointage

class PointageForm(forms.ModelForm):
    class Meta:
        model = Pointage
        fields = ['volume_realise', 'observation']

class DemarrageForm(forms.ModelForm):
    class Meta:
        model = ClasseProgression
        fields = ['enseignant']


from django import forms
from .models import DossierMinistere

class DossierMinistereForm(forms.ModelForm):
    class Meta:
        model = DossierMinistere
        fields = [
            'matricule_etudiant', 'nom', 'prenom', 'date_de_naissance', 
            'filiere', 'extrait_de_naissance', 'justificatif_d_identite', 
            'collante_du_bac', 'telephone'
        ]
        widgets = {
            'matricule_etudiant': forms.TextInput(attrs={'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'date_de_naissance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'filiere': forms.Select(attrs={'class': 'form-select'}),  # Dropdown select
            'extrait_de_naissance': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'justificatif_d_identite': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'collante_du_bac': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer les filières selon l'établissement avec id = 5
        self.fields['filiere'].queryset = Filiere.objects.filter(etablissement_id=1)

    def clean_extrait_de_naissance(self):
        file = self.cleaned_data.get('extrait_de_naissance')
        self.validate_pdf(file)
        return file

    def clean_justificatif_d_identite(self):
        file = self.cleaned_data.get('justificatif_d_identite')
        self.validate_pdf(file)
        return file

    def clean_collante_du_bac(self):
        file = self.cleaned_data.get('collante_du_bac')
        self.validate_pdf(file)
        return file

    @staticmethod
    def validate_pdf(file):
        if not file.name.endswith('.pdf'):
            raise forms.ValidationError("Le document doit être en format PDF.")
        if file.content_type != 'application/pdf':
            raise forms.ValidationError("Le fichier soumis n'est pas un PDF.")


# Formulaire filtré par l'établissement de l'utilisateur

class ClasseForm(forms.ModelForm):
    class Meta:
        model = Classe
        fields = ['annee_academique', 'filiere', 'niveau', 
                  'classe_universitaire', 'classe_professionnelle_jour', 
                  'classe_professionnelle_soir', 'classe_online']
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Ajouter la classe CSS "form-control" à tous les champs
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

        if user:
            self.fields['filiere'].queryset = Filiere.objects.filter(etablissement=user.etablissement)
            self.fields['niveau'].queryset = Niveau.objects.filter(etablissement=user.etablissement)
            self.fields['annee_academique'].queryset = AnneeAcademique.objects.filter(etablissement=user.etablissement)


from .models import Diplome

class DiplomeForm(forms.ModelForm):
    class Meta:
        model = Diplome
        fields = [
            'nom', 
            'prenom', 
            'date_de_naissance', 
            'lieu_de_naissance', 
            'sexe', 
            'contact1', 
            'contact2', 
            'diplome', 
            'niveau', 
            'annee_academique', 
            'date_soutenance', 
            'session_soutenance', 
            'cycle']
    def __init__(self, *args, **kwargs):
        super(DiplomeForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'



class EtablissementForm(forms.ModelForm):
    class Meta:
        model = Etablissement
        fields = [
            "nom",
            "sigle",
            "code",
            "full_name",
            "logo",
            "cachet_scolarite",
            "footer_bull",
            "contact",
            "email",
            "site",
            "is_college",
            "active",
            "wave_api_key",
        ]
        widgets = {
            "full_name": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
            "footer_bull": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "nom": forms.TextInput(attrs={"class": "form-control"}),
            "sigle": forms.TextInput(attrs={"class": "form-control"}),
            "code": forms.TextInput(attrs={"class": "form-control"}),
            "contact": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "site": forms.URLInput(attrs={"class": "form-control"}),
            "wave_api_key": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "is_college": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["nom"].label = "Nom de l'établissement"
        self.fields["sigle"].label = "Sigle"
        self.fields["code"].label = "Code interne"
        self.fields["full_name"].label = "Dénomination complète"
        self.fields["logo"].label = "Logo"
        self.fields["cachet_scolarite"].label = "Cachet scolarité"
        self.fields["footer_bull"].label = "Pied de page des bulletins"
        self.fields["contact"].label = "Contact"
        self.fields["email"].label = "Email"
        self.fields["site"].label = "Site web"
        self.fields["is_college"].label = "Est un collège ?"
        self.fields["active"].label = "Établissement actif ?"
        self.fields["wave_api_key"].label = "Clé API Wave (optionnel)"
