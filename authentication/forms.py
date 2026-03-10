from django import forms
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from .models import User

class UserCreationForm(BaseUserCreationForm):
    class Meta(BaseUserCreationForm.Meta):
        model = User
        fields = ('nom', 'prenom', 'email', 'is_medecin', 'is_stock', 'can_view_stock', 'can_register_student', 'can_register_teacher', 'can_view_teacher_profile_and_contrat', 'can_view_teacher_acccompte','is_transport', 'can_manage_teacher_acccompte','can_make_emargement', 'can_manage_fees', 'can_update_fees', 'can_add_note', 'can_update_time', 'can_view_index_summary','is_super_admin',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control', 'style': 'border: 2px solid black;'})