from django import forms
from django.contrib import admin
from .models import User
from gestion_academique.models import Classe

# Formulaire personnalisé pour l'Admin
class UserAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'


# Admin pour User
from django import forms
from django.contrib import admin
from .models import User
from gestion_academique.models import Classe

# Formulaire personnalisé pour l'Admin
class UserAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        # Récupérer l'utilisateur connecté à partir du contexte
        request = kwargs.pop('request', None)
        super(UserAdminForm, self).__init__(*args, **kwargs)
        
        # Filtrer les classes par l'établissement de l'utilisateur connecté
        if request and request.user.etablissement:
            self.fields['classe'].queryset = Classe.objects.filter(
                etablissement=request.user.etablissement
            )

# Admin pour User
class UserAdmin(admin.ModelAdmin):
    form = UserAdminForm
    search_fields = ["nom", "prenom", "etablissement__nom"]
    list_display = ("email", "nom", "prenom", "etablissement", "is_student", "is_teacher", 
                    "is_staff", "is_active", 'can_register_student', 'can_register_teacher', 'can_update_fees')
    filter_horizontal = ('classe',)  # Pour afficher les classes sous forme de cases à cocher

    def get_queryset(self, request):
        # Récupérer l'établissement de l'utilisateur connecté
        etablissement = request.user.etablissement
        # Filtrer les utilisateurs en fonction de l'établissement de l'utilisateur connecté
        queryset = User.objects.filter(etablissement=etablissement)
        return queryset

    def get_form(self, request, obj=None, **kwargs):
        # Passer l'objet request au formulaire pour avoir accès à l'utilisateur connecté
        kwargs['form'] = self.form
        form = super(UserAdmin, self).get_form(request, obj, **kwargs)
        form.request = request
        return form
    
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "classe":
            kwargs["queryset"] =  Classe.objects.filter(
                annee_academique__etablissement=request.user.etablissement
            )
        return super(UserAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

# Enregistrer l'Admin
admin.site.register(User, UserAdmin)


