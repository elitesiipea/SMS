from django.db import models

# Create your models here.
class Resume(models.Model):
    """Model definition for Resume."""
    etudiant = models.OneToOneField("etudiants.Etudiant", on_delete=models.CASCADE)
    fonction = models.CharField(max_length=150)
    a_propos = models.TextField(default="")
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    # TODO: Define fields here

    class Meta:
        """Meta definition for Resume."""

        verbose_name = 'Resume'
        verbose_name_plural = 'Resumes'

    def __str__(self):
        """Unicode representation of Resume."""
        return f'{self.etudiant}'

    @property
    def experiences(self):
        return self.resume_info.filter(nature__exact="EXPERIENCE PROFESSIONNELLE").order_by('created')

    @property
    def educations(self):
        return self.resume_info.filter(nature__exact="EDUCATION").order_by('created')

    @property
    def competences(self):
        return self.resume_data.filter(nature__exact="COMPETENCE").order_by('created')
    
    @property
    def loisirs(self):
        return self.resume_data.filter(nature__exact="LOISIR").order_by('created')

    @property
    def autres(self):
        return self.resume_data.filter(nature__exact="AUTRES").order_by('created')

    @property
    def langues(self):
        return self.resume_data.filter(nature__exact="LANGUE").order_by('created')

    @property
    def atouts(self):
        return self.resume_data.filter(nature__exact="ATOUT").order_by('created')


    # TODO: Define custom methods here

type_info = (
        ('EXPERIENCE PROFESSIONNELLE', 'EXPERIENCE PROFESSIONNELLE',),
        ('EDUCATION', 'EDUCATION',),
)


class Information(models.Model):
    """Model definition for Information."""
    resume = models.ForeignKey(Resume, related_name="resume_info", on_delete=models.CASCADE)
    nature = models.CharField(max_length=100, choices=type_info,)
    intitule = models.CharField(max_length=250, help_text="Nom de la structure")
    etablissement = models.CharField(max_length=100, help_text="Nom de la structure ou a eu lieu l'activité")
    debut = models.CharField(max_length=100, help_text="Date de debut de l'activité")
    fin = models.CharField(max_length=100, help_text="Date de fin de l'activité")
    description = models.TextField(help_text="Description de l'activité",default="")
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    # TODO: Define fields here

    class Meta:
        """Meta definition for Information."""

        verbose_name = 'Information'
        verbose_name_plural = 'Informations'

    def __str__(self):
        """Unicode representation of Information."""
        return f'{self.resume.etudiant}'


    # TODO: Define custom methods here

type_data = (

        ('COMPETENCE', 'COMPETENCE',),
        ('LOISIR', 'LOISIR',),
        ('LANGUE', 'LANGUE',),
        ('ATOUT', 'ATOUT',),
        ('AUTRES', 'AUTRES',),
)

class Data(models.Model):
    """Model definition for Data."""
    resume = models.ForeignKey(Resume, related_name="resume_data", on_delete=models.CASCADE)
    nature = models.CharField(max_length=50, choices=type_data,)
    intitule = models.CharField(max_length=250, help_text="Titre de l'information")
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    # TODO: Define fields here

    class Meta:
        """Meta definition for Data."""

        verbose_name = 'Data'
        verbose_name_plural = 'Datas'

    def __str__(self):
        """Unicode representation of Data."""
        return f'{self.intitule}'

    # TODO: Define custom methods here
