from django import forms
from .models import Information, Data, Resume

class InformationForm(forms.ModelForm):
    class Meta:
        model = Information
        fields = ('nature', 'intitule', 'etablissement', 'debut', 'fin', 'description', )
        
    def __init__(self, *args, **kwargs):
        super(InformationForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control nature_id required-field' , 'style' : 'border:1px solid black'})

class DataForm(forms.ModelForm):
    class Meta:
        model = Data
        fields = ('nature', 'intitule', )
    def __init__(self, *args, **kwargs):
        super(DataForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control nature_id required-field' , 'style' : 'border:1px solid black'})

class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ('a_propos','fonction')
    def __init__(self, *args, **kwargs):
        super(ResumeForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control nature_id required-field', 'style' : 'border:1px solid black'})