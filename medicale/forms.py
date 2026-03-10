from django import forms
from .models import Consultation, DossierMedical

class ConsultationForm(forms.ModelForm):
    class Meta:
        model = Consultation
        exclude = ['dossier','medecin', 'created', 'date_update','annee_academique']

    def __init__(self, *args, **kwargs):
        super(ConsultationForm, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control required', 'style':'border: 2px solid black'})

        for field_name, field in self.fields.items():
            if field_name in ['rendez_vous','debut_arret_travail', 'fin_arret_travail',]:
                field.widget.attrs.update({
                                            'class': 'form-control datepicker-here required',
                                            'id':"default-date",
                                            "placeholder":"dd/mm/yyyy",
                                            "aria-describedby":"basic-addon2",
                                            })


class DossierMedicalForm(forms.ModelForm):
    class Meta:
        model = DossierMedical
        fields = ('hta', 'diabete', 'asthme', 'drepanocytose', 'ulcere', 'epilepsie', 'autre_antecedents', 
                  'pere_hta', 'pere_diabete', 'pere_asthme', 'pere_drepanocytose', 'pere_ulcere', 'pere_epilepsie', 'pere_autre_antecedents', 
                  'mere_hta', 'mere_diabete', 'mere_asthme', 'mere_drepanocytose', 'mere_ulcere', 'mere_epilepsie', 'mere_autre_antecedents', 
                  'tabac', 'alcool', 'stupefiant', )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Champs regroupés par section et disposés en deux colonnes
        section1_fields = [
            
            'hta', 'diabete', 'asthme', 'drepanocytose',
            'ulcere', 'epilepsie', 'autre_antecedents'
        ]
        section2_fields = [
            'pere_hta', 'pere_diabete', 'pere_asthme', 'pere_drepanocytose', 'pere_ulcere',
            'pere_epilepsie', 'pere_autre_antecedents'
        ]
        section3_fields = [
            'mere_hta', 'mere_diabete', 'mere_asthme', 'mere_drepanocytose', 'mere_ulcere',
            'mere_epilepsie', 'mere_autre_antecedents'
        ]
        section4_fields = ['tabac', 'alcool', 'stupefiant']

        self.fieldsets = [
            ('Étudiant', {'fields': section1_fields}),
            ('Père', {'fields': section2_fields}),
            ('Mère', {'fields': section3_fields}),
            ('État de vie', {'fields': section4_fields}),
            
        ]

        for name, options in self.fieldsets:
            fields = options['fields']
            for field in fields:
                form_field = self.fields[field]
                form_field.widget.attrs['class'] = 'form-control'
                if field == 'etudiant':
                    form_field.widget.attrs['readonly'] = True

    def as_fieldsets(self):
        for name, options in self.fieldsets:
            yield {
                'name': name,
                'fields': [self[field] for field in options['fields']],
            }