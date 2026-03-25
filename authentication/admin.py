from django import forms
from django.contrib import admin
from .models import User
from gestion_academique.models import Classe


class UserAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        user = getattr(self.request, "user", None)
        etablissement = getattr(user, "etablissement", None)

        if etablissement and "classe" in self.fields:
            self.fields["classe"].queryset = Classe.objects.filter(
                annee_academique__etablissement=etablissement
            )


class UserAdmin(admin.ModelAdmin):
    form = UserAdminForm
    search_fields = ["nom", "prenom", "etablissement__nom"]
    list_display = (
        "email",
        "nom",
        "prenom",
        "etablissement",
        "is_student",
        "is_teacher",
        "is_staff",
        "is_active",
        "can_register_student",
        "can_register_teacher",
        "can_update_fees",
    )
    filter_horizontal = ("classe", "gestion")

    def get_queryset(self, request):
        etablissement = getattr(request.user, "etablissement", None)
        if etablissement and not request.user.is_superuser:
            return User.objects.filter(etablissement=etablissement)
        return User.objects.all()

    def get_form(self, request, obj=None, **kwargs):
        Form = super().get_form(request, obj, **kwargs)

        class RequestForm(Form):
            def __init__(self2, *args, **kw):
                kw["request"] = request
                super().__init__(*args, **kw)

        return RequestForm

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        etablissement = getattr(request.user, "etablissement", None)

        if db_field.name == "classe":
            if etablissement and not request.user.is_superuser:
                kwargs["queryset"] = Classe.objects.filter(
                    annee_academique__etablissement=etablissement
                )

        return super().formfield_for_manytomany(db_field, request, **kwargs)


admin.site.register(User, UserAdmin)


