from django import forms
from .models import DemoRequest
class DemoRequestForm(forms.ModelForm):
    class Meta:
        model = DemoRequest
        fields = [
            "full_name",
            "position",
            "school_name",
            "school_type",
            "email",
            "phone",
            "students_count",
            "preferred_slot",
            "message",
        ]
        widgets = {
            "message": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "w-full rounded-2xl bg-slate-950/80 border border-slate-700/70 px-3 py-2 text-xs text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-1 focus:ring-secondary",
                    "placeholder": "Présentez rapidement votre contexte actuel, vos outils, vos attentes…",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base_class = "w-full rounded-2xl bg-slate-950/80 border border-slate-700/70 px-3 py-2 text-xs text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-1 focus:ring-secondary"
        for name, field in self.fields.items():
            if name == "message":
                continue
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} {base_class}".strip()
            if not field.widget.attrs.get("placeholder"):
                field.widget.attrs["placeholder"] = field.label
