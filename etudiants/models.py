from django.db import models
from django.urls import reverse
from django_countries.fields import CountryField
import secrets
import sys
import string
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile




status_etudiant = (
    ('Affecté(e)', 'Affecté(e)',),
    ('Non Affecté(e)', 'Non Affecté(e)',),
)

sexes = (
        ('Masculin', 'Masculin',),
        ('Feminin', 'Feminin',),
)

status_etablissement = (
        ('PRIVE', 'PRIVE',),
        ('PUBLIC', 'PUBLIC',),
)

class EtablissementDorigine(models.Model):
    """Model definition for EtablissementDorigine."""
    code = models.CharField(max_length=10)
    nom = models.CharField(max_length=200)
    dren = models.CharField(max_length=100)
    type_etablissement = models.CharField(max_length=20, choices=status_etablissement)
    statut = models.CharField(max_length=10, default="MIXTE")

    # TODO: Define fields here

    class Meta:
        """Meta definition for EtablissementDorigine."""

        verbose_name = 'Etablissement Dorigine'
        verbose_name_plural = "Etablissements D'origines"
        ordering = ['nom',]

    def __str__(self):
        """Unicode representation of EtablissementDorigine."""
        return self.nom


    # TODO: Define custom methods here



class Etudiant(models.Model):
    """Model definition for Etudiant."""
    utilisateur = models.OneToOneField("authentication.User", on_delete=models.CASCADE)
    nom = models.CharField(max_length=120)
    prenom = models.CharField(max_length=120)
    type_etudiant = models.CharField(max_length=14, choices=status_etudiant,)
    etablissement = models.ForeignKey('gestion_academique.Etablissement', related_name="etudiant_etablissement", on_delete=models.CASCADE)
    etablissement_d_origine = models.ForeignKey(EtablissementDorigine, related_name="etudiant_etablissement_origine", on_delete=models.CASCADE)
    date_de_naissance = models.DateField()
    lieu_de_naissance = models.CharField(max_length=50)
    matricule_mers = models.CharField(max_length=50)
    numero_table_bac = models.CharField(max_length=50)
    matricule_menet = models.CharField(max_length=50)
    nationalite = CountryField(blank_label='(Selectionner le pays)')
    matricule = models.CharField(max_length=50, editable=True,null=True, blank=True)
    lieu_de_residence = models.CharField(max_length=50)
    sexe = models.CharField(max_length=10, choices=sexes,)
    serie_bac = models.CharField(max_length=10)
    contact = models.CharField(max_length=10)
    contactparent = models.CharField(max_length=10)
    photo = models.FileField(upload_to='etudiant/photo',null=True, blank=True)
    extrait = models.FileField(upload_to='etudiant/extrait',null=True, blank=True)
    diplome = models.FileField(upload_to='etudiant/diplome',null=True, blank=True)
    fiche_orientation =models.FileField(upload_to='etudiant/fiche_orientation',null=True, blank=True)
    piece = models.FileField(upload_to='etudiant/piece',null=True, blank=True)
    dictaticiel = models.BooleanField(default=False)
    sans_bac = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    extrait_depose = models.BooleanField(default=False)
    cmu = models.BooleanField(default=False)
    piece_depose = models.BooleanField(default=False)
    photo_depose = models.BooleanField(default=False)
    diplome_depose = models.BooleanField(default=False)
    fiche_orientation_depose = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    carte_etudiant = models.BooleanField(default=False)
    date_update = models.DateTimeField(auto_now=True)
    code_paiement  = models.CharField(max_length=10,editable=False)
    photo_updated = models.BooleanField(default=False)

    # TODO: Define fields here

    class Meta:
        """Meta definition for Etudiant."""

        verbose_name = 'Etudiant'
        verbose_name_plural = 'Etudiants'

    def __str__(self):
        """Unicode representation of Etudiant."""
        return f'{self.utilisateur.nom} {self.utilisateur.prenom}'

    def save(self, *args, **kwargs):
        # Check if the matricule is already set, i.e., it's an existing object being updated
        image = Image.open(self.photo)
        output = BytesIO()

            # Resize the image
        new_size = (225, 250)
        image = image.resize(new_size)

            # Save the resized image to the output buffer
        image.save(output, format='PNG', quality=100)
        output.seek(0)

            # Create an InMemoryUploadedFile and assign it to the model field
        self.photo = InMemoryUploadedFile(
                output,
                'ImageField',
                f"{self.photo.name.split('.')[0]}_resized.png",
                'image/png',
                sys.getsizeof(output),
                None
        )
           
        if not self.matricule:
            # Generate the matricule using the provided logic
            nom_initials = self.nom.replace(" ", "")[:3]
            prenom_initial = self.prenom.split()[0][0]
            day = str(self.date_de_naissance.day).zfill(2)
            month = str(self.date_de_naissance.month).zfill(2)
            year_last_two_digits = str(self.date_de_naissance.year)[-2:]
            base_matricule = f"{nom_initials.upper()}{prenom_initial.upper()}{day}{month}{year_last_two_digits}"

            # Get the maximum matricule in the database with the same base_matricule
            max_matricule_with_base = Etudiant.objects.filter(matricule__startswith=base_matricule).order_by('-matricule').first()

            # If there are existing matricules with the same base_matricule, increment the counter
            if max_matricule_with_base:
                last_counter = int(max_matricule_with_base.matricule[-4:])
                new_counter = last_counter + 1
            else:
                new_counter = 1

            # Create the final matricule by adding the counter at the end
            self.matricule = f"{base_matricule}{str(new_counter).zfill(4)}"

        if not self.code_paiement:
            # Generate a random 10-character alphanumeric code
            chars = (string.ascii_uppercase + string.digits).upper()
            self.code_paiement = ''.join(secrets.choice(chars) for _ in range(10))

            # Ensure the code is unique in the database
            while Etudiant.objects.filter(code_paiement=self.code_paiement).exists():
                self.code_paiement = ''.join(secrets.choice(chars) for _ in range(10))

        super(Etudiant, self).save(*args, **kwargs)
        

    def url(self):
        return reverse('etudiant_profile', args=[str(self.pk)])
        

    def scolarite_admin_url(self):
        return reverse('student_inscription_list', args=[str(self.code_paiement)])

    def carte(self):
        return reverse('carte_validated',kwargs={'pk': self.pk})

        

    # TODO: Define custom methods here

    @property
    def last_class(self):
        return self.inscription_etudiant.order_by('-created').first()
    
class SessionSoutenanceNew(models.Model):
    """Model definition for SessionSoutenanceNew."""
    titre = models.CharField(max_length=150)
    etablissement = models.ForeignKey('gestion_academique.Etablissement', related_name="session_etablissement", on_delete=models.CASCADE)
    fichier = models.FileField(upload_to='soutenance/fichier',null=True, blank=True)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    carte_etudiant = models.BooleanField(default=False)
    date_update = models.DateTimeField(auto_now=True)
    code = models.CharField(max_length=28)
    ss = models.CharField(max_length=28, blank=True, null=True,)

    # TODO: Define fields here

    class Meta:
        """Meta definition for SessionSoutenanceNew."""

        verbose_name = 'Session Soutenance'
        verbose_name_plural = 'Session Soutenances'

    def __str__(self):
        """Unicode representation of SessionSoutenanceNew."""
        return f'{self.titre}'
    
    @property
    def candidats(self):
        return self.AttestationNew_session.all().order_by('nom')
    
    @property
    def candidats_nb(self):
        return self.candidats.all().count()
    
    
    def save(self, *args, **kwargs):

        if not self.code:
            # Generate a random 50-character alphanumeric code
            chars = (string.ascii_uppercase + string.digits).upper()
            self.code = ''.join(secrets.choice(chars) for _ in range(28))

            # Ensure the code is unique in the database
            while SessionSoutenanceNew.objects.filter(code=self.code).exists():
                self.code = ''.join(secrets.choice(chars) for _ in range(28))

        super(SessionSoutenanceNew, self).save(*args, **kwargs)

    # TODO: Define custom methods here





class AttestationNew(models.Model):
    """Model definition for AttestationNew."""
    session = models.ForeignKey(SessionSoutenanceNew, related_name="AttestationNew_session", on_delete=models.CASCADE)
    nom = models.CharField(max_length=150)
    prenom = models.CharField(max_length=150)
    sexe = models.CharField(max_length=50)
    matricule = models.CharField(max_length=50)
    date_de_naissance = models.DateField()
    lieu_de_naissance = models.CharField(max_length=150)
    pays = models.CharField(max_length=150)
    filiere = models.CharField(max_length=150)
    cycle = models.CharField(max_length=150)
    niveau = models.CharField(max_length=150)
    annee_academique = models.CharField(max_length=150)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    carte_etudiant = models.BooleanField(default=False)
    date_update = models.DateTimeField(auto_now=True)
    code = models.CharField(max_length=28)
    ss = models.CharField(max_length=28, blank=True, null=True,)

    # TODO: Define fields here

    class Meta:
        """Meta definition for AttestationNew."""

        verbose_name = 'AttestationNew'
        verbose_name_plural = 'AttestationNews'

    def __str__(self):
        """Unicode representation of AttestationNew."""
        return f'{self.nom} {self.prenom}'

    def url(self):
        """Return absolute url for AttestationNew."""
        return ('')
    
    def save(self, *args, **kwargs):

        if not self.code:
            # Generate a random 50-character alphanumeric code
            chars = (string.ascii_uppercase + string.digits).upper()
            self.code = ''.join(secrets.choice(chars) for _ in range(12))

            # Ensure the code is unique in the database
            while AttestationNew.objects.filter(code=self.code).exists():
                self.code = ''.join(secrets.choice(chars) for _ in range(12))

        super(AttestationNew, self).save(*args, **kwargs)

    # TODO: Define custom methods here



class SessionDiplome(models.Model):
    """Model definition for SessionSoutenanceNew."""
    titre = models.CharField(max_length=150)
    etablissement = models.ForeignKey('gestion_academique.Etablissement', related_name="session_diplome_etablissement", on_delete=models.CASCADE)
    fichier = models.FileField(upload_to='diplome/fichier',null=True, blank=True)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    carte_etudiant = models.BooleanField(default=False)
    date_update = models.DateTimeField(auto_now=True)
    code = models.CharField(max_length=28)
    ss = models.CharField(max_length=28, blank=True, null=True,)

    # TODO: Define fields here

    class Meta:
        """Meta definition for SessionSoutenanceNew."""

        verbose_name = 'Session Diplome'
        verbose_name_plural = 'Session Diplome'

    def __str__(self):
        """Unicode representation of Diplome."""
        return f'{self.titre}'
    
    @property
    def candidats(self):
        return self.Diplome_session.all()
    
    @property
    def candidats_nb(self):
        return self.candidats.count()
    
    
    def save(self, *args, **kwargs):

        if not self.code:
            # Generate a random 50-character alphanumeric code
            chars = (string.ascii_uppercase + string.digits).upper()
            self.code = ''.join(secrets.choice(chars) for _ in range(28))

            # Ensure the code is unique in the database
            while SessionDiplome.objects.filter(code=self.code).exists():
                self.code = ''.join(secrets.choice(chars) for _ in range(28))

        super(SessionDiplome, self).save(*args, **kwargs)

    # TODO: Define custom methods here



class Diplome(models.Model):
    """Model definition for AttestationNew."""
    session = models.ForeignKey(SessionDiplome, related_name="Diplome_session", on_delete=models.CASCADE)
    nom = models.CharField(max_length=150)
    prenom = models.CharField(max_length=150)
    diplome = models.CharField(max_length=150)
    date_de_naissance =  models.DateField()
    lieu_de_naissance = models.CharField(max_length=150)
    cycle = models.CharField(max_length=150)
    niveau = models.CharField(max_length=150)
    annee_academique = models.CharField(max_length=150)
    active = models.BooleanField(default=True)
    code = models.CharField(max_length=28)
    programme = models.CharField(max_length=28)
   

    # TODO: Define fields here

    class Meta:
        """Meta definition for AttestationNew."""

        verbose_name = 'Diplome'
        verbose_name_plural = 'Diplomes'

    def __str__(self):
        """Unicode representation of AttestationNew."""
        return f'{self.nom} {self.prenom}'

    def url(self):
        """Return absolute url for AttestationNew."""
        return ('')
    
    def save(self, *args, **kwargs):

        if not self.code:
            # Generate a random 50-character alphanumeric code
            chars = (string.ascii_uppercase + string.digits).upper()
            self.code = ''.join(secrets.choice(chars) for _ in range(12))

            # Ensure the code is unique in the database
            while Diplome.objects.filter(code=self.code).exists():
                self.code = ''.join(secrets.choice(chars) for _ in range(12))

        super(Diplome, self).save(*args, **kwargs)

    # TODO: Define custom methods here




class CertificatSession(models.Model):
    """Model definition for SessionSoutenanceNew."""
    titre = models.CharField(max_length=150)
    etablissement = models.ForeignKey('gestion_academique.Etablissement', related_name="session_certificat_etablissement", on_delete=models.CASCADE)
    fichier = models.FileField(upload_to='diplome/fichier',null=True, blank=True)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    carte_etudiant = models.BooleanField(default=False)
    date_update = models.DateTimeField(auto_now=True)
    code = models.CharField(max_length=28)
    ss = models.CharField(max_length=28, blank=True, null=True,)

    # TODO: Define fields here

    class Meta:
        """Meta definition for SessionSoutenanceNew."""

        verbose_name = 'Certificat Session'
        verbose_name_plural = 'Certificat Session'

    def __str__(self):
        """Unicode representation of Diplome."""
        return f'{self.titre}'
    
    @property
    def candidats(self):
        return self.certificat_session.all()
    
    @property
    def candidats_nb(self):
        return self.candidats.count()
    
    
    def save(self, *args, **kwargs):

        if not self.code:
            # Generate a random 50-character alphanumeric code
            chars = (string.ascii_uppercase + string.digits).upper()
            self.code = ''.join(secrets.choice(chars) for _ in range(28))

            # Ensure the code is unique in the database
            while CertificatSession.objects.filter(code=self.code).exists():
                self.code = ''.join(secrets.choice(chars) for _ in range(28))

        super(CertificatSession, self).save(*args, **kwargs)

    # TODO: Define custom methods here



class Certificat(models.Model):
    """Model definition for AttestationNew."""
    session = models.ForeignKey(CertificatSession, related_name="certificat_session", on_delete=models.CASCADE)
    nom = models.CharField(max_length=150)
    prenom = models.CharField(max_length=150)
    diplome = models.CharField(max_length=150)
    date_de_naissance =  models.DateField()
    lieu_de_naissance = models.CharField(max_length=150)
    cycle = models.CharField(max_length=150)
    niveau = models.CharField(max_length=150)
    annee_academique = models.CharField(max_length=150)
    active = models.BooleanField(default=True)
    code = models.CharField(max_length=28)
    programme = models.CharField(max_length=28)
   

    # TODO: Define fields here

    class Meta:
        """Meta definition for AttestationNew."""

        verbose_name = 'Certificat'
        verbose_name_plural = 'Certificats'

    def __str__(self):
        """Unicode representation of AttestationNew."""
        return f'{self.nom} {self.prenom}'

    def url(self):
        """Return absolute url for AttestationNew."""
        return ('')
    
    def save(self, *args, **kwargs):

        if not self.code:
            # Generate a random 50-character alphanumeric code
            chars = (string.ascii_uppercase + string.digits).upper()
            self.code = ''.join(secrets.choice(chars) for _ in range(12))

            # Ensure the code is unique in the database
            while Certificat.objects.filter(code=self.code).exists():
                self.code = ''.join(secrets.choice(chars) for _ in range(12))

        super(Certificat, self).save(*args, **kwargs)

    # TODO: Define custom methods here