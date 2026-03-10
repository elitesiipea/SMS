from django.db import models

# Create your models here.
class DossierMedical(models.Model):
    """Model definition for DossierMedical."""
    #fieldset etudiant
    etudiant = models.OneToOneField("etudiants.Etudiant", on_delete=models.CASCADE)
    hta = models.BooleanField(default=False)
    diabete = models.BooleanField(default=False)
    asthme = models.BooleanField(default=False)
    drepanocytose = models.BooleanField(default=False)
    ulcere = models.BooleanField(default=False)
    epilepsie = models.BooleanField(default=False)
    autre_antecedents = models.CharField(max_length=250, null=True, blank=True)
    #fieldset pere
    pere_hta = models.BooleanField(default=False)
    pere_diabete = models.BooleanField(default=False)
    pere_asthme = models.BooleanField(default=False)
    pere_drepanocytose = models.BooleanField(default=False)
    pere_ulcere = models.BooleanField(default=False)
    pere_epilepsie = models.BooleanField(default=False)
    pere_autre_antecedents = models.CharField(max_length=250, null=True, blank=True)
    #fieldset mere
    mere_hta = models.BooleanField(default=False)
    mere_diabete = models.BooleanField(default=False)
    mere_asthme = models.BooleanField(default=False)
    mere_drepanocytose = models.BooleanField(default=False)
    mere_ulcere = models.BooleanField(default=False)
    mere_epilepsie = models.BooleanField(default=False)
    mere_autre_antecedents = models.CharField(max_length=250, null=True, blank=True)
    #fieldset etat de vie
    tabac = models.BooleanField(default=False)
    alcool = models.BooleanField(default=False)
    stupefiant = models.BooleanField(default=False)
    #fieldset date
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    code = models.CharField(max_length=50, null=True, blank=True)


    # TODO: Define fields here

    class Meta:
        """Meta definition for DossierMedical."""

        verbose_name = 'Dossier Medical'
        verbose_name_plural = 'Dossier Medicals'

    def __str__(self):
        """Unicode representation of DossierMedical."""
        return str(self.etudiant)

    # TODO: Define custom methods here

    @property
    def consultations(self):
        return self.dossier_consultations.all().order_by('-created')

class Consultation(models.Model):
    """Model definition for Consultation."""
    medecin = models.ForeignKey('authentication.User', related_name="medecin_consultations", on_delete=models.CASCADE)
    annee_academique = models.ForeignKey('gestion_academique.AnneeAcademique', related_name="annee_consultations", on_delete=models.CASCADE)
    dossier = models.ForeignKey(DossierMedical, related_name="dossier_consultations", on_delete=models.CASCADE)
    #fieldset constante
    TA = models.CharField(max_length=50)
    pouls = models.CharField(max_length=50)
    Temperature = models.CharField(max_length=50)
    FR = models.CharField(max_length=50)
    Sao2 = models.CharField(max_length=50)
    Glasgow = models.CharField(max_length=50)
    poids = models.CharField(max_length=3, blank=True, null=True)
    #fieldset données
    motif_de_la_consultation = models.TextField(null=True, blank=True)
    histoire_de_la_mamdie = models.TextField(null=True, blank=True)
    examen_physique = models.TextField(null=True, blank=True)
    hypotheses_diagnostic = models.TextField(null=True, blank=True)
    examens_paracliniques = models.TextField(null=True, blank=True)
    diagnostic_retenu = models.TextField(null=True, blank=True)
    traitement = models.TextField(null=True, blank=True)
    evolution = models.TextField(null=True, blank=True)
    #fieldset arret maladie
    rendez_vous  = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
    arret_de_travail = models.BooleanField(default=False)
    debut_arret_travail  = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
    fin_arret_travail  = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
    #fieldset date
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)


    # TODO: Define fields here

    class Meta:
        """Meta definition for Consultation."""

        verbose_name = 'Consultation'
        verbose_name_plural = 'Consultations'

    def __str__(self):
        """Unicode representation of Consultation."""
        return f'{self.dossier.etudiant} : Dr {self.medecin} {self.created}'

