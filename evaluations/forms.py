from django import forms
from .models import Note
from enseignant.models import ContratEnseignant
from .models import Resultat

class ResultatForm(forms.ModelForm):
    class Meta:
        model = Resultat
        fields = ['etudiant','note_1', 'note_2', 'note_3','note_partiel', 'non_classe', 'session']

    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control' , 'style' : 'border:2px solid black'})

        self.fields['etudiant'].widget.attrs.update({'readonly': 'readonly'})

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        exclude = ['coefficient_note_partiel', 'coeeficient_matiere', 'classe','active', 'created', 'date_update',]

    def __init__(self,classe,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exemple : Personnalisation d'une étiquette
        self.fields['use_note_1'].label = "Utiliser la note 1"
        self.fields['matiere'].label = "Sélectionner la matière"
        self.fields['use_note_1'].label = "Utiliser la note 1"
        self.fields['use_note_2'].label = "Utiliser la note 2"
        self.fields['use_note_3'].label = "Utiliser la note 3"
        self.fields['use_note_partiel'].label = "Utiliser la note du partiel"
        self.fields['partiel_uniquement'].label = "Uniquement la note du partiel"

        self.fields['matiere'].queryset = ContratEnseignant.objects.filter(
            classe_id=classe).order_by('matiere__nom', 'matiere__unite__semestre')

        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control' , 'style' : 'border:2px solid black'})

