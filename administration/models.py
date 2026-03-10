from django.db import models


class DemoRequest(models.Model):
    """
    Représente une demande de démo de SMS (School Management System).
    Utilisé pour garder un historique des leads entrants.
    """

    SCHOOL_TYPES = [
        ("MATERNELLE", "École maternelle"),
        ("PRIMAIRE", "École primaire"),
        ("SECONDAIRE", "Collège / Lycée"),
        ("SUPERIEUR", "Enseignement supérieur / Université"),
        ("FORMATION", "Centre de formation"),
        ("AUTRE", "Autre"),
    ]

    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    position = models.CharField(
        max_length=120,
        help_text="Ex: Proviseur, Directeur, Responsable pédagogique, Comptable…",
        blank=True,
    )
    school_name = models.CharField(max_length=200)
    school_type = models.CharField(max_length=20, choices=SCHOOL_TYPES, default="AUTRE")
    students_count = models.CharField(
        max_length=50,
        blank=True,
        help_text="Ex: 300, 500–1000, +2000…",
    )
    preferred_slot = models.CharField(
        max_length=100,
        blank=True,
        help_text="Ex: Lundi matin, Soir après les cours, Week-end…",
    )
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Demande de démo – {self.full_name} ({self.school_name})"