from django.db import models


jours = (
    ('LUNDI', 'LUNDI'),
    ('MARDI', 'MARDI'),
    ('MERCREDI', 'MERCREDI'),
    ('JEUDI', 'JEUDI'),
    ('VENDREDI', 'VENDREDI'),
    ('SAMEDI', 'SAMEDI'),
    ('DIMANCHE', 'DIMANCHE'),
)

# Create your models here.
class EmploisDutemps(models.Model):
    '''Model definition for EmploisDutemps.'''
    classe = models.OneToOneField("gestion_academique.Classe", related_name="classe_programme", on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    class Meta:
        '''Meta definition for EmploisDutemps.'''

        verbose_name = 'Emplois Du temps'
        verbose_name_plural = 'Emplois Du temps'

    def __str__(self):
        return f'{self.classe} {self.classe.annee_academique}'


    def get_absolute_url(self):
        '''Return absolute url for EmploisDutemps.'''
        return ('')


jours = (
    ('LUNDI', 'LUNDI'),
    ('MARDI', 'MARDI'),
    ('MERCREDI', 'MERCREDI'),
    ('JEUDI', 'JEUDI'),
    ('VENDREDI', 'VENDREDI'),
    ('SAMEDI', 'SAMEDI'),
    ('DIMANCHE', 'DIMANCHE'),
)

class Programme(models.Model):
    """Model definition for Programme."""
    emplois_du_temps = models.ForeignKey(EmploisDutemps, related_name="emplois_du_temps_matiere", on_delete=models.CASCADE)
    date = models.DateField(auto_now=False, auto_now_add=False)
    matiere = models.CharField(max_length=255)
    salle = models.CharField(max_length=255)
    jour = models.CharField(max_length=10, choices=jours,)
    debut = models.CharField(max_length=255)
    fin = models.CharField(max_length=255)
    enseignant = models.CharField(max_length=255, null=True, blank=True)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    
    # emplois_du_temps = models.ForeignKey(EmploisDutemps, related_name="emplois_du_temps_matiere", on_delete=models.CASCADE)
    # date = models.DateField(auto_now=False, auto_now_add=False)
    # matiere = models.ForeignKey('enseignant.ContratEnseignant', related_name="emplois_du_temps_matiere", on_delete=models.CASCADE)
    # salle = models.ForeignKey('gestion_academique.Salle', related_name="salle_cours", on_delete=models.CASCADE)
    # jour = models.CharField(max_length=10, choices=jours,)
    # debut = models.TimeField(auto_now=False, auto_now_add=False)
    # fin = models.TimeField(auto_now=False, auto_now_add=False)
    # active = models.BooleanField(default=True)
    # created = models.DateTimeField(auto_now_add=True)
    # date_update = models.DateTimeField(auto_now=True)

    # TODO: Define fields here

    class Meta:
        """Meta definition for Programme."""

        verbose_name = 'Programme'
        verbose_name_plural = 'Programmes'
        ordering = ['date']

    def __str__(self):
        """Unicode representation of Programme."""
        return f'{self.emplois_du_temps} {self.matiere}'

    # def save(self, *args, **kwargs):
    #     """
    #     Save method for Programme.
    #     Perform additional checks before saving the object.
    #     """
    #     # Vérifier s'il existe un autre objet Programme avec les mêmes caractéristiques
    #     existing_programme = Programme.objects.filter(
    #         emplois_du_temps=self.emplois_du_temps,
    #         matiere=self.matiere,
    #         salle=self.salle,
    #         jour=self.jour,
    #         debut=self.debut,
    #         fin=self.fin,
    #     ).exclude(pk=self.pk)  # Exclure l'objet actuel lors de la recherche des doublons

    #     if existing_programme.exists():
    #         pass

    #     # Vérifier s'il existe un autre objet Programme avec la même salle et des heures chevauchantes
    #     overlapping_programmes = Programme.objects.filter(
    #         salle=self.salle,
    #         jour=self.jour,
    #         debut__lt=self.fin,
    #         fin__gt=self.debut,
    #     ).exclude(pk=self.pk)  # Exclure l'objet actuel lors de la recherche des chevauchements

    #     if overlapping_programmes.exists():
    #         pass

    #     # Si aucune violation n'a été détectée, continuez avec la sauvegarde normale
    #     else:
    #         super().save(*args, **kwargs)


    def get_absolute_url(self):
        """Return absolute url for Programme."""
        return ('')

    # TODO: Define custom methods here
