from django import forms
from .models import EmploisDutemps, Programme
from gestion_academique.models import  Salle
from enseignant.models import ContratEnseignant

class ProgrammeForm(forms.ModelForm):
    class Meta:
        model = Programme
        fields = ('jour','date','matiere','enseignant', 'salle',  'debut', 'fin')

    def __init__(self, id_etablissement, classe_id ,  *args, **kwargs):
        super(ProgrammeForm, self).__init__(*args, **kwargs)
        self.fields['matiere'].queryset  = ContratEnseignant.objects.filter(classe_id=classe_id)
        self.fields['salle'].queryset  = Salle.objects.filter(etablissement_id=id_etablissement)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control nature_id required-field', 'style' : 'border:1px solid black'})

        for field_name, field in self.fields.items():
            if field_name == "date":
                field.widget.attrs.update({
                                            'class': 'form-control datepicker-here required',
                                            'id':"default-date",
                                            "placeholder":"dd/mm/yyyy",
                                            "aria-describedby":"basic-addon2",
                                            })