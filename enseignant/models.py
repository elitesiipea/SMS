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
# Create your models here.
class Enseignant(models.Model):
    """Model definition for Enseignant."""
    utilisateur = models.OneToOneField("authentication.User", on_delete=models.CASCADE)
    nom = models.CharField(max_length=120)
    prenom = models.CharField(max_length=120)
    email = models.EmailField(max_length=254)
    etablissement = models.ForeignKey('gestion_academique.Etablissement', related_name="enseignant_etablissement", on_delete=models.CASCADE)
    cv_et_document  = models.FileField(upload_to='enseignant/dossier',null=True, blank=True)
    domaine = models.TextField()
    numero_cni = models.CharField(max_length=50)
    date_de_naissance = models.DateField()
    lieu_de_naissance = models.CharField(max_length=50)
    nationalite = CountryField(blank_label='(Selectionner le pays)')
    domicile = models.CharField(max_length=50)
    statut_enseignant = models.CharField(max_length=50, choices=statuts,)
    sexe = models.CharField(max_length=50, choices=sexes,)
    situations = models.CharField(max_length=50, choices=situations,)
    contact = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    code  = models.CharField(max_length=50,editable=False)
    # TODO: Define fields here

    class Meta:
        """Meta definition for Enseignant."""

        verbose_name = 'Enseignant'
        verbose_name_plural = 'Enseignants'

    def __str__(self):
        """Unicode representation of Enseignant."""
        return f'{self.utilisateur}'

    def save(self, *args, **kwargs):
        
        if not self.code:
            # Generate a random 10-character alphanumeric code
            chars = (string.ascii_uppercase + string.digits).upper()
            self.code = ''.join(secrets.choice(chars) for _ in range(10))

            # Ensure the code is unique in the database
            while Enseignant.objects.filter(code=self.code).exists():
                self.code = ''.join(secrets.choice(chars) for _ in range(10))

        super(Enseignant, self).save(*args, **kwargs)

    def url(self):
        return reverse('enseignant_profile', args=[str(self.code)])

    def contrat_url(self):
        
        return reverse('contrat_enseignant_list_admin', args=[str(self.code)])



        

    # TODO: Define custom methods here


class ContratEnseignant(models.Model):

    """Model definition for ContratEnseignant."""
    annee_academique = models.ForeignKey("gestion_academique.AnneeAcademique", related_name="annee_contrat", on_delete=models.CASCADE)
    enseignant = models.ForeignKey(Enseignant, related_name="enseignant_contrat", on_delete=models.CASCADE, null=True, blank=True)
    filiere = models.ForeignKey("gestion_academique.Filiere", related_name="filiere_contrat", on_delete=models.CASCADE,  null=True, blank=True)
    niveau = models.ForeignKey("gestion_academique.Niveau", related_name="niveau_contrat", on_delete=models.CASCADE, null=True, blank=True)
    classe = models.ForeignKey("gestion_academique.Classe", related_name="classe_contrat", on_delete=models.CASCADE,  null=True, blank=True)
    matiere =models.ForeignKey("gestion_academique.Matiere", related_name="matiere_contrat", on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField()
    volume_horaire = models.FloatField(default=0)
    progression = models.FloatField(default=0)
    taux_horaire = models.IntegerField(default=0)
    support = models.FileField(upload_to='cours/support',null=True, blank=True)
    syllabus = models.FileField(upload_to='cours/syllabus',null=True, blank=True)
    support_depose = models.BooleanField(default=False)
    syllabus_depose = models.BooleanField(default=False)
    cahier_de_texte = models.BooleanField(default=False)
    notes = models.BooleanField(default=False)
    closed = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    demande_accompte = models.BooleanField(default=False)
    demande_traitee = models.BooleanField(default=False)
    numero_cheque  = models.CharField(max_length=50)
    cheque_retire = models.BooleanField(default=False)


    # TODO: Define fields here

    class Meta:
        """Meta definition for ContratEnseignant."""

        verbose_name = 'Contrat Enseignant'
        verbose_name_plural = 'Contrat Enseignants'
        ordering = ['matiere__unite__semestre','matiere__nom']

    def __str__(self):
        """Unicode representation of ContratEnseignant."""
        return f'{self.matiere} ({self.enseignant})'.upper()

    def cours_url(self):
        return reverse('course_details', kwargs={'code' : self.enseignant.code , 'pk' : self.pk })

    def can_demande(self):
        return self.closed and self.syllabus_depose and self.support_depose and self.cahier_de_texte and self.notes

    @property
    def cout(self):
        return round(self.taux_horaire * self.volume_horaire)
    
    @property
    def td(self):
        td = TravauxDirige.objects.filter(contrat_id=self.id).last()
        return td

        
    @property
    def have_td(self):
        td = TravauxDirige.objects.filter(contrat_id=self.id)
        if td :
            return True
        else:
            return False
    
    def save(self, *args, **kwargs):
        # Check if the matricule is already set, i.e., it's an existing object being updated
        if self.cheque_retire:
            if self.td:
                self.td.paye = True 
                self.td.save()
        

        super(ContratEnseignant, self).save(*args, **kwargs)
        

    


    # TODO: Define custom methods here


class TravauxDirige(models.Model):
    """Model definition for TravauxDirige."""
    contrat = models.OneToOneField(ContratEnseignant, related_name="contratd_td", on_delete=models.CASCADE)
    volume_horaire = models.FloatField(default=0)
    taux_horaire = models.IntegerField(default=0)
    progression = models.FloatField(default=0)
    paye = models.BooleanField(default=False)
    
    # TODO: Define fields here

    class Meta:
        """Meta definition for TravauxDirige."""

        verbose_name = 'Travaux Dirige'
        verbose_name_plural = 'Travaux Diriges'

    def __str__(self):
        """Unicode representation of TravauxDirige."""
        return 'TD {} {} Heure(s)'.format(self.contrat, self.volume_horaire)

    def get_absolute_url(self):
        """Return absolute url for TravauxDirige."""
        return ('')
    
    @property
    def cout(self):
        return self.volume_horaire * self.taux_horaire

    # TODO: Define custom methods here


class Rib(models.Model):
    """Model definition for Rib."""
    enseignant = models.ForeignKey(Enseignant, related_name="enseignant_rib", on_delete=models.CASCADE, null=True, blank=True)
    banque = models.CharField(max_length=50)
    document = models.FileField(upload_to='enseignants/rib',null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    default = models.BooleanField(default=True)

    # TODO: Define fields here

    class Meta:
        """Meta definition for Rib."""

        verbose_name = 'Rib'
        verbose_name_plural = 'Ribs'

    def __str__(self):
        """Unicode representation of Rib."""
        return "{}{}".format(self.banque)

    def save(self, *args, **kwargs):
        """Save method for Rib."""
        # Check if there are other Ribs for the same enseignant
        existing_ribs = Rib.objects.filter(enseignant=self.enseignant)
        
        # If there are existing Ribs, set their default to False
        if existing_ribs.exists():
            existing_ribs.update(default=False)
        
        # Call the original save method to save the current Rib
        super().save(*args, **kwargs)

    # TODO: Define custom methods here
