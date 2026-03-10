from django.db import models
from cloudinary.models import CloudinaryField
from django.contrib import messages
from django.urls import reverse
from emplois_du_temps.models import EmploisDutemps
import secrets
import sys
import string


cycles = (

    ('CONTINU', 'CONTINU',),
    ('ONLINE', 'ONLINE',),
    ('PROFESSIONNEL', 'PROFESSIONNEL',),
    ('UNIVERSITAIRE', 'UNIVERSITAIRE',),

)

cycles_diplomes = (

    ('PROFESSIONNEL', 'PROFESSIONNEL',),
    ('UNIVERSITAIRE', 'UNIVERSITAIRE',),

)

niveau_diplomes = (

    ('LICENCE', 'LICENCE',),
    ('MASTER', 'MASTER',),

)

type_filieres = (

    ('UNIVERSITAIRE', 'UNIVERSITAIRE',),
    ('PROFESSIONNEL', 'PROFESSIONNEL',),
    

)

jours = (
        ('Lundi', 'Lundi',),
        ('Mardi', 'Mardi',),
        ('Mercredi', 'Mercredi',),
        ('Jeudi', 'Jeudi',),
        ('Vendredi', 'Vendredi',),
        ('Samedi', 'Samedi',),
        ('Dimanche', 'Dimanche',),
)

session = (
    ('SESSION 1', 'SESSION 1',),
    ('SESSION 2', 'SESSION 2',)

)

semestre = (
    ('SEMESTRE 1', 'SEMESTRE 1',),
    ('SEMESTRE 2', 'SEMESTRE 2',),
    ('SEMESTRE 3', 'SEMESTRE 3',)

)

categories_ue = (

    ('CONNAISSANCE FONDEMENTALE', 'CONNAISSANCE FONDEMENTALE',),
    ('METHODOLOGIE', 'METHODOLOGIE',),
    ('CULTURE GENERALE', 'CULTURE GENERALE',),

)

class Etablissement(models.Model):
    """Model definition for Etablissement."""
    nom = models.CharField(max_length=150)
    sigle = models.CharField(max_length=150)
    code = models.CharField(max_length=150)
    full_name = models.TextField()
    logo = models.FileField(upload_to='etablissement/logo',null=True, blank=True)
    cachet_scolarite = models.FileField(upload_to='etablissement/cachez_scolarite',null=True, blank=True)
    footer_bull = models.TextField()
    contact = models.CharField(max_length=254)
    email = models.EmailField(max_length=254)
    site = models.EmailField(max_length=254)
    active = models.BooleanField(default=True)
    is_college = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    wave_api_key = models.TextField(null=True, blank=True)

    # TODO: Define fields here

    class Meta:
        """Meta definition for Etablissement."""

        verbose_name = 'Etablissement'
        verbose_name_plural = 'Etablissements'

    def __str__(self):
        """Unicode representation of Etablissement."""
        return self.full_name
    
    @property
    def salles_count(self):
        return sum(item.places_total for item in self.campus.all())
    
class Campus(models.Model):
    """Model definition for Campus."""
    etablissement = models.ForeignKey(Etablissement, on_delete=models.CASCADE, related_name="campus")
    nom = models.CharField(max_length=50)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    # TODO: Define fields here

    class Meta:
        """Meta definition for Campus."""

        verbose_name = 'Campus'
        verbose_name_plural = 'Campuss'

    def __str__(self):
        """Unicode representation of Campus."""
        return self.nom


    def get_absolute_url(self):
        """Return absolute url for Campus."""
        return ('')
    
    @property
    def salles(self):
        return self.salle_campus.all().order_by('nom')
    
    @property
    def salles_count(self):
        return self.salles.count()
    
    @property
    def places_total(self):
        return sum(item.capacite for item in self.salles)

    # TODO: Define custom methods here



class Salle(models.Model):
    """Model definition for Salle."""
    etablissement = models.ForeignKey(Etablissement, on_delete=models.CASCADE, related_name="salles")
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="salle_campus")
    nom = models.CharField(max_length=50)
    capacite = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    # TODO: Define fields here

    class Meta:
        """Meta definition for Salle."""

        verbose_name = 'Salle'
        verbose_name_plural = 'Salles'

    def __str__(self):
        """Unicode representation of Salle."""
        return f'{self.nom}'

    # TODO: Define custom methods here


class AnneeAcademique(models.Model):
    """Model definition for AnneeAcademique."""
    etablissement = models.ForeignKey(Etablissement, on_delete=models.CASCADE, related_name="annee_academiques")
    debut = models.IntegerField()
    fin = models.IntegerField()
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    # TODO: Define fields here

    class Meta:
        """Meta definition for AnneeAcademique."""

        verbose_name = 'Année Academique'
        verbose_name_plural = 'Années Academiques'

    def __str__(self):
        """Unicode representation of AnneeAcademique."""
        return f'{self.debut} - {self.fin}'

    @property
    def annees(self):
        """Unicode representation of AnneeAcademique."""
        return f'{self.debut}-{self.fin}'

    @property
    def etudiants(self):
        return self.inscription_annee.filter(confirmed=True).count()
    
    @property
    def effectes(self):
        return self.inscription_annee.filter(confirmed=True, etudiant__type_etudiant__exact="Affecté(e)" ).count()
    
    @property
    def non_effectes(self):
        return self.inscription_annee.filter(confirmed=True, etudiant__type_etudiant__exact="Non Affecté(e)" ).count()
    
    @property
    def univ(self):
        return self.inscription_annee.filter(confirmed=True, parcour__exact="CYCLE UNIVERSITAIRE" ).count()
    
    @property
    def pro(self):
        return self.inscription_annee.filter(confirmed=True, parcour__exact="CYCLE PROFESSIONNEL JOUR").count()
    
    @property
    def fc(self):
        return self.inscription_annee.filter(confirmed=True, parcour__exact="CYCLE PROFESSIONNEL SOIR").count()
    

    @property
    def to_json(self):
        return {
            "debut": self.debut,
            "fin": self.fin,
            "etudiants": self.etudiants,
            # Vous pouvez ajouter d'autres champs ici si nécessaire
        }
    # TODO: Define custom methods here
    #  

class Filiere(models.Model):
    """Model definition for Filiere."""
    etablissement = models.ForeignKey(
        Etablissement, related_name="etablissement_filiere", on_delete=models.CASCADE)
    nom = models.CharField(max_length=200)
    parcour = models.CharField(max_length=200, choices=type_filieres)
    sigle = models.CharField(max_length=10)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    # TODO: Define fields here

    class Meta:
        """Meta definition for Filiere."""

        verbose_name = 'Filiere'
        verbose_name_plural = 'Filieres'
        ordering = ['nom']

    def __str__(self):
        """Unicode representation of Filiere."""
        return self.nom

    # TODO: Define custom methods here


class Niveau(models.Model):
    """Model definition for Niveau."""
    etablissement = models.ForeignKey(Etablissement, related_name="etablissement_niveau", on_delete=models.CASCADE)
    nom = models.CharField(max_length=200)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    # TODO: Define fields here

    class Meta:
        """Meta definition for Niveau."""

        verbose_name = 'Niveau'
        verbose_name_plural = 'Niveaux'

    def __str__(self):
        """Unicode representation of Niveau."""
        return self.nom


    # TODO: Define custom methods here


class Classe(models.Model):
    """Model definition for Classe."""
    nom = models.CharField(max_length=50)
    annee_academique = models.ForeignKey(
        AnneeAcademique, on_delete=models.CASCADE, related_name="classe_annee_academique")
    filiere = models.ForeignKey(
        Filiere, on_delete=models.CASCADE, related_name="classe_filiere")
    niveau = models.ForeignKey(
        Niveau, on_delete=models.CASCADE, related_name="classe_niveau")
    
    classe_universitaire = models.BooleanField(
        default=False, help_text='Cochez si la classe est une classe universitaire')
    classe_professionnelle_jour = models.BooleanField(
        default=False, help_text='Cochez si la classe est une classe professionnelle jour')
    classe_professionnelle_soir = models.BooleanField(
        default=False, help_text='Cochez si la classe est une classe professionnelle soir')
    classe_online = models.BooleanField(
        default=False, help_text='Cochez si la classe est une classe en ligne')
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    closed = models.BooleanField(default=True)
    date_update = models.DateTimeField(auto_now=True)
    # TODO: Define fields here

    class Meta:
        """Meta definition for Classe."""

        verbose_name = 'Classe'
        verbose_name_plural = 'Classes'
        ordering = ['nom']
        
    @property
    def cycle(self):
        if self.classe_universitaire:
            return "UNIVERSITAIRE"
        if self.classe_professionnelle_soir:
            return "PRO SOIR"
        if self.classe_professionnelle_jour:
            return "PRO JOUR"
        if self.classe_online:
            return "ONLINE"

    def __str__(self):
        """Unicode representation of AnneeAcademique."""
        return f'{self.nom} ({self.cycle} - {self.annee_academique.debut} - {self.annee_academique.fin})'

    @property
    def programmations(self):
        return self.classe_contrat.all()

    @property
    def volume_global(self):
        return sum(item.volume_horaire for item in self.programmations)

    @property
    def cout_global(self):
        return sum(item.cout for item in self.programmations)


    @property
    def volume_effectue(self):
        return sum(item.progression for item in self.programmations)

    @property
    def progression(self):
        if self.volume_global == 0:
            return 0
        return round((self.volume_effectue * 100) / self.volume_global)
    
    




    def save(self, *args, **kwargs):
        if not self.pk:
            # Get the filiere and niveau of the class
            if not self.annee_academique:
                self.annee_academique = self.filiere.etablissement.annee_academiques.latest()
            
            filiere = self.filiere
            sigle = self.filiere.sigle
            niveau = self.niveau

            # Check if the name is already set (for modifications)
            if not self.nom:
                # Retrieve existing class names with the same filiere and niveau
                existing_classes = Classe.objects.filter(filiere=filiere, niveau=niveau).values_list('nom', flat=True)
                
                # Find an available letter from A to Z to append to the class name
                alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                for letter in alphabet:
                    class_name_with_letter = f"{sigle} {niveau} {letter}"

                    if class_name_with_letter not in existing_classes:
                        # Set the unique name with the letter appended
                        self.nom = class_name_with_letter
                        break

        super(Classe, self).save(*args, **kwargs)

        # Ensure that EmploisDutemps is updated or created after the class is saved
        EmploisDutemps.objects.get_or_create(classe=self)
        

    def get_absolute_url(self):
        """Return absolute url for Classe."""
        return ('')

    # TODO: Define custom methods here


    @property
    def effectifs(self):
        return self.inscription_classe.all().order_by('etudiant__nom', 'etudiant__prenom')

    @property
    def nb_etudiant(self):
        return self.effectifs.count()

    def url(self):
        return reverse('classes_details', args=[str(self.pk)])

        


class Maquette(models.Model):
    """Model definition for Maquette."""
    etablissement = models.ForeignKey('Etablissement', related_name="maquette_etablissement", on_delete=models.CASCADE)
    annee_academique = models.ForeignKey(AnneeAcademique, on_delete=models.CASCADE, related_name="maquette_annee_academemique")
    filiere = models.ForeignKey('Filiere', related_name="maquette_filiere", on_delete=models.CASCADE)
    niveau = models.ForeignKey('Niveau', related_name="maquette_niveau", on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    maquette_universitaire = models.BooleanField(default=False)
    maquette_professionnel_jour = models.BooleanField(default=False)
    maquette_professionnel_soir = models.BooleanField(default=False)
    maquette_cours_en_ligne = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    # TODO: Define fields here

    class Meta:
        """Meta definition for Maquette."""

        verbose_name = 'Maquette'
        verbose_name_plural = 'Maquettes'

    def __str__(self):
        """Unicode representation of Maquette."""
        return f'{self.filiere} {self.niveau}'
    
    def url_to_edit_object(obj):
        url = reverse('admin:%s_%s_change' % (obj._meta.app_label,  obj._meta.model_name),  args=[obj.id])
        return url

    def save(self, *args, **kwargs):
        # Check if an object with the same filiere and niveau exists
        existing_maquette = Maquette.objects.filter(
            filiere=self.filiere, 
            niveau=self.niveau, 
            annee_academique=self.annee_academique,
            maquette_universitaire=self.maquette_universitaire,
            maquette_professionnel_jour=self.maquette_professionnel_jour,
            maquette_professionnel_soir=self.maquette_professionnel_soir,
            maquette_cours_en_ligne=self.maquette_cours_en_ligne
            
            ).exists()

        if existing_maquette:
            # If the object exists, do not save and raise an exception
            pass
            
        else:
            # If the object doesn't exist, save it
            super(Maquette, self).save(*args, **kwargs)

    def url(self):
        return reverse('maquette_details', args=[str(self.pk)])

    @property 
    def unites(self):
        return self.ue_maquette.all()

    @property 
    def unites_s1(self):
        return self.ue_maquette.filter(semestre__exact="SEMESTRE 1")
    

    @property 
    def unites_s2(self):
        return self.ue_maquette.filter(semestre__exact="SEMESTRE 2")
    
    @property 
    def unites_s3(self):
        return self.ue_maquette.filter(semestre__exact="SEMESTRE 3")

    @property 
    def unites_count(self):
        return self.unites.count()

    @property 
    def matieres(self):
        return self.matiere_maquette.all()

    @property 
    def matiere_count(self):
        return self.matieres.count()



    @property 
    def matiere_1(self):
        return self.matiere_maquette.filter(unite__semestre__exact="SEMESTRE 1")

    @property 
    def matiere_1_count(self):
        return self.matiere_1.count()

    @property 
    def matiere_2(self):
        return self.matiere_maquette.filter(unite__semestre__exact="SEMESTRE 2")

    @property 
    def matiere_2_count(self):
        return self.matiere_2.count()
    
    @property 
    def matiere_3(self):
        return self.matiere_maquette.filter(unite__semestre__exact="SEMESTRE 3")

    @property 
    def matiere_3_count(self):
        return self.matiere_3.count()


    @property
    def cout(self):
        return sum(item.cout for item in self.matiere_maquette.all()) + sum(item.cout_td for item in self.matiere_maquette.all())

    @property
    def volume_global(self):
        return sum(item.volume_horaire for item in self.matiere_maquette.all()) + sum(item.volume_horaire_td for item in self.matiere_maquette.all())
    
    @property
    def volumeS1(self):
        return sum(item.volume_horaire for item in self.matiere_1)
    
    @property
    def volumeS2(self):
        return sum(item.volume_horaire for item in self.matiere_2)
    
    @property
    def volumeS1_td(self):
        return sum(item.volume_horaire_td for item in self.matiere_1)
    
    @property
    def volumeS2_td(self):
        return sum(item.volume_horaire_td for item in self.matiere_2)
    
    @property
    def volumeS3(self):
        return sum(item.volume_horaire for item in self.matiere_3)
    
    @property
    def volumeS3_td(self):
        return sum(item.volume_horaire_td for item in self.matiere_3)
    
    @property
    def coutS1(self):
        return sum(item.cout for item in self.matiere_1)
    
    @property
    def coutS2(self):
        return sum(item.cout for item in self.matiere_2)
    
    @property
    def coutS1_td(self):
        return sum(item.cout_td for item in self.matiere_1)
    
    @property
    def coutS2_td(self):
        return sum(item.cout_td for item in self.matiere_2)
    
    @property
    def coutS3_td(self):
        return sum(item.cout_td for item in self.matiere_3)
    
    @property
    def coutS3(self):
        return sum(item.cout for item in self.matiere_3)
    # TODO: Define custom methods here
    
    @property
    def credit_1(self):
        return sum(item.coefficient for item in self.matiere_1)
    
    @property
    def credit_2(self):
        return sum(item.coefficient for item in self.matiere_2)
    
    @property
    def credit_3(self):
        return sum(item.coefficient for item in self.matiere_3)


class UniteEnseignement(models.Model):
    """Model definition for UniteEnseignement."""
    maquette = models.ForeignKey(Maquette, related_name="ue_maquette", on_delete=models.CASCADE)
    nom = models.CharField(max_length=200)
    semestre = models.CharField(max_length=200, choices=semestre)
    categorie = models.CharField(max_length=200, choices=categories_ue)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    # TODO: Define fields here

    class Meta:
        """Meta definition for UniteEnseignement."""

        verbose_name = 'Unité Enseignement'
        verbose_name_plural = 'Unités Enseignements'

    def __str__(self):
        """Unicode representation of UniteEnseignement."""
        return f'{self.maquette.filiere} {self.maquette.niveau} {self.nom} {self.semestre}'


    def get_absolute_url(self):
        """Return absolute url for UniteEnseignement."""
        return ('')

    @property
    def matieres(self):
        return self.matiere_ue.all()

    @property
    def matieres_count(self):
        return self.matieres.count()
        
    @property
    def credit(self):
        return sum(item.coefficient for item in self.matieres)

    # TODO: Define custom methods here


class Matiere(models.Model):
    """Model definition for Matiere."""
    maquette = models.ForeignKey(Maquette, related_name="matiere_maquette", on_delete=models.CASCADE)
    nom = models.CharField(max_length=200)
    unite = models.ForeignKey(UniteEnseignement, related_name="matiere_ue", on_delete=models.CASCADE)
    nom = models.CharField(max_length=200)
    enseignant = models.CharField(max_length=50, null=True, blank=True)
    contact_enseignant = models.CharField(max_length=50, null=True, blank=True)
    coefficient = models.IntegerField()
    volume_horaire = models.IntegerField(default=0)
    taux_horaire = models.IntegerField(default=0)
    volume_horaire_td = models.IntegerField(default=0)
    taux_horaire_td = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
   

    # TODO: Define fields here

    class Meta:
        """Meta definition for Matiere."""

        verbose_name = 'Matiere'
        verbose_name_plural = 'Matieres'

    def __str__(self):
        """Unicode representation of Matiere."""
        return f'{self.nom} {self.unite.semestre[-1]} '


    def get_absolute_url(self):
        """Return absolute url for Matiere."""
        return ('')

    @property
    def cout(self):
        return self.taux_horaire * self.volume_horaire
    
    @property
    def cout_td(self):
        return self.taux_horaire_td * self.volume_horaire_td
    
    @property
    def volume_total(self):
        return self.volume_horaire + self.volume_horaire_td
    # TODO: Define custom methods here


class StudentMessage(models.Model):
    """Model definition for StudentMessage."""
    etablissement = models.ForeignKey(Etablissement, on_delete=models.CASCADE, related_name="messages")
    titre = models.CharField(max_length=50)
    message = models.TextField()
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    # TODO: Define fields here

    class Meta:
        """Meta definition for StudentMessage."""

        verbose_name = 'Message'
        verbose_name_plural = 'Messages'

    def __str__(self):
        """Unicode representation of StudentMessage."""
        return f'{self.titre} {self.etablissement}'
    
    


class SessionDiplome(models.Model):
    """Model definition for SessionSoutenanceNew."""
    titre = models.CharField(max_length=150)
    etablissement = models.ForeignKey('gestion_academique.Etablissement', related_name="session_diplome_etablissements", on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
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
        return self.Diplome_session_two.all()
    
    @property
    def candidats_nb(self):
        return self.candidats.count()
    


class Diplome(models.Model):
    """Model definition for Diplome."""

    # TODO: Define fields here
    session = models.ForeignKey(SessionDiplome, related_name="Diplome_session_two", on_delete=models.CASCADE)
    matricule = models.CharField(max_length=50)
    nom = models.CharField(max_length=155)
    prenom = models.CharField(max_length=155)
    date_de_naissance = models.DateField(auto_now=False, auto_now_add=False)
    lieu_de_naissance = models.CharField(max_length=155)
    sexe = models.CharField(max_length=50, blank=True, null=True)
    contact1 = models.CharField(max_length=50, blank=True, null=True)
    contact2 = models.CharField(max_length=50, blank=True, null=True)
    diplome = models.CharField(max_length=155)
    niveau = models.CharField(max_length=50, choices=niveau_diplomes)
    annee_academique = models.CharField(max_length=50)
    date_soutenance = models.CharField(max_length=50)
    session_soutenance = models.CharField(max_length=50)
    cycle = models.CharField(max_length=50, choices=cycles_diplomes)
    code = models.CharField(max_length=50, null=True, blank=True)
    
    

    class Meta:
        """Meta definition for Diplome."""

        verbose_name = 'Diplome'
        verbose_name_plural = 'Diplomes'

    def __str__(self):
        """Unicode representation of Diplome."""
        return "{} {}".format(self.nom, self.prenom)
    
    @property
    def genre(self):
        if self.sexe == "MASCULIN":
            return " Monsieur "
        return " Madame / Mademoiselle "

    def save(self, *args, **kwargs):

        if not self.code:
            # Generate a random 50-character alphanumeric code
            chars = (string.ascii_uppercase + string.digits).upper()
            self.code = ''.join(secrets.choice(chars) for _ in range(12))

            # Ensure the code is unique in the database
            while Diplome.objects.filter(code=self.code).exists():
                self.code = ''.join(secrets.choice(chars) for _ in range(12))

        super(Diplome, self).save(*args, **kwargs)

    def get_absolute_url(self):
        """Return absolute url for Diplome."""
        return ('')

    # TODO: Define custom methods here

def generate_unique_code():
    import uuid
    return str(uuid.uuid4())[:8]

