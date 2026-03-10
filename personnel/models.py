from django.db import models
import secrets
import string
from datetime import datetime
from cloudinary.models import CloudinaryField
from django.contrib import messages
from django.urls import reverse
from django_countries.fields import CountryField
from django.core.exceptions import ValidationError

sexes = (
        ('Masculin', 'Masculin',),
        ('Feminin', 'Feminin',),
)

situations = (
    ('Célibataire', 'Célibataire',),
    ('Veuf(ve)', 'Veuf(ve)',),
    ('Marié(e)', 'Marié(e)',),
    ('Divorcé(e)', 'Divorcé(e)',),
)

statuts = (
    ('Titulaire', 'Titulaire',),
    ('Vacataire', 'Vacataire',),


)

class Service(models.Model):
    """Model definition for Service."""
 #   etablissement = models.ForeignKey('gestion_academique.Etablissement', related_name="service_etablissement", on_delete=models.CASCADE)
    nom = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    # TODO: Define fields here

    class Meta:
        """Meta definition for Service."""

        verbose_name = 'Service'
        verbose_name_plural = 'Services'

    def __str__(self):
        """Unicode representation of Service."""
        return self.nom


# Create your models here.
class PersonnelAdministratif(models.Model):
    """Model definition for Enseignant."""
    utilisateur = models.OneToOneField("authentication.User", on_delete=models.CASCADE)
    nom = models.CharField(max_length=120)
    prenom = models.CharField(max_length=120)
    email = models.EmailField(max_length=254)
    etablissement = models.ForeignKey('gestion_academique.Etablissement', related_name="personnel_etablissement", on_delete=models.CASCADE)
    cv_et_document  = models.FileField(upload_to='enseignant/dossier',null=True, blank=True)
    service = models.ForeignKey(Service, related_name="personnel_service", on_delete=models.CASCADE)
    numero_cni = models.CharField(max_length=50)
    date_de_naissance = models.DateField()
    lieu_de_naissance = models.CharField(max_length=50)
    nationalite = CountryField(blank_label='(Selectionner le pays)')
    domicile = models.CharField(max_length=50)
    sexe = models.CharField(max_length=10, choices=sexes,)
    situations = models.CharField(max_length=20, choices=situations,)
    contact = models.CharField(max_length=10)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    code  = models.CharField(max_length=10,editable=False)
    # TODO: Define fields here

    class Meta:
        """Meta definition for Personnel Administratif."""

        verbose_name = 'Personnel Administratif'
        verbose_name_plural = 'Personnel Administratif'

    def __str__(self):
        """Unicode representation of Personnel Administratif."""
        return f'{self.utilisateur}'

    def save(self, *args, **kwargs):
        
        if not self.code:
            # Generate a random 10-character alphanumeric code
            chars = (string.ascii_uppercase + string.digits).upper()
            self.code = ''.join(secrets.choice(chars) for _ in range(10))

            # Ensure the code is unique in the database
            while PersonnelAdministratif.objects.filter(code=self.code).exists():
                self.code = ''.join(secrets.choice(chars) for _ in range(10))

        super(PersonnelAdministratif, self).save(*args, **kwargs)

    def url(self):
        return reverse('personnel_profile', args=[str(self.code)])


