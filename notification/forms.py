from django import forms
from .models import Notification

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ('titre','description')
        # Vous pouvez personnaliser les champs affichés dans le formulaire


    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control' , 'style' : 'border:2px solid black'})