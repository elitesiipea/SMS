from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse

session = (
    ('SESSION 1', 'SESSION 1'),
    ('SESSION 2', 'SESSION 2'),
)

class Note(models.Model):
    """Model definition for Note."""
    classe = models.ForeignKey('gestion_academique.Classe', related_name="classe_note", on_delete=models.CASCADE)
    matiere = models.ForeignKey('enseignant.ContratEnseignant', related_name="note_matiere", on_delete=models.CASCADE)
    use_note_1 = models.BooleanField(default=True, help_text="Cocher si la note 1 est prise en compte")
    use_note_2 = models.BooleanField(default=True, help_text="Cocher si la note 2 est prise en compte")
    use_note_3 = models.BooleanField(default=True, help_text="Cocher si la note 3 est prise en compte")
    use_note_partiel = models.BooleanField(default=True, help_text="Cocher si la note du partiel est prise en compte")
    partiel_uniquement = models.BooleanField(default=False, help_text="Cocher si uniquement la note du partiel est prise en compte")
    fichier = models.FileField(upload_to='notes/fichiers/')
    coefficient_note_partiel = models.IntegerField(default=1)
    coeeficient_matiere  = models.IntegerField(default=1)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'

    def __str__(self):
        return f'{self.classe} {self.matiere}'

    def save(self, *args, **kwargs):
        if not self.pk:
            self.coeeficient_matiere = self.matiere.matiere.coefficient
            if self.classe.classe_universitaire:
                self.coefficient_note_partiel = 2
        super().save(*args, **kwargs)

    def url(self):
        return reverse('evaluation_details', kwargs={'classe_id': self.classe.id, 'pk': self.pk})


class Resultat(models.Model):
    """Model definition for Resultat."""
    note = models.ForeignKey(Note, related_name="note_resultat", on_delete=models.CASCADE)
    etudiant = models.ForeignKey("inscription.Inscription", related_name="insription_note", on_delete=models.CASCADE)
    note_1 = models.FloatField(default=0, validators=[MaxValueValidator(20), MinValueValidator(0)])
    note_2 = models.FloatField(default=0, validators=[MaxValueValidator(20), MinValueValidator(0)])
    note_3 = models.FloatField(default=0, validators=[MaxValueValidator(20), MinValueValidator(0)])
    note_partiel = models.FloatField(default=0, validators=[MaxValueValidator(20), MinValueValidator(0)])
    non_classe = models.BooleanField(default=False, help_text="Cocher si l'étudiant est non classé dans la matière")
    session = models.CharField(max_length=10, choices=session, default="SESSION 1")
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    moyenne = models.FloatField(default=0, editable=False)
    moyenne_coefficient = models.FloatField(default=0, editable=False)
    moyenne_unite = models.FloatField(default=0, editable=False)

    @property
    def moyenne_calculee(self):
        """Calcul dynamique de la moyenne"""
        if self.non_classe:
            return None  # Exclu du calcul
        notes_utilisees = sum([self.note.use_note_1, self.note.use_note_2, self.note.use_note_3, self.note.use_note_partiel])
        total_notes = sum([
            self.note_1 * self.note.use_note_1,
            self.note_2 * self.note.use_note_2,
            self.note_3 * self.note.use_note_3,
            self.note_partiel * self.note.use_note_partiel
        ])
        return round(total_notes / notes_utilisees, 2) if notes_utilisees > 0 else 0

    @property
    def moyenne_coefficient_calculee(self):
        """Calcul dynamique de la moyenne pondérée par le coefficient"""
        if self.non_classe:
            return None
        return round(self.moyenne_calculee * self.note.coeeficient_matiere, 2)

    @property
    def moyenne_unite_calculee(self):
        """Moyenne des matières d'une même unité d'enseignement"""
        notes = Resultat.objects.filter(
            etudiant=self.etudiant,
            note__matiere__matiere__unite=self.note.matiere.matiere.unite,
            non_classe=False  # Exclure les non classés
        )
        return round(sum(item.moyenne_calculee for item in notes if item.moyenne_calculee is not None) / notes.count(), 2) if notes.exists() else 0

    def save(self, *args, **kwargs):
        """Calcul de la moyenne avant sauvegarde"""
        if self.non_classe:
            self.moyenne = 0
            self.moyenne_coefficient = 0
            self.moyenne_unite = 0
        else:
            self.moyenne = self.moyenne_calculee or 0
            self.moyenne_coefficient = self.moyenne_coefficient_calculee or 0

            notes_unite = Resultat.objects.filter(
                etudiant=self.etudiant,
                note__matiere__matiere__unite=self.note.matiere.matiere.unite,
                non_classe=False  # Exclure les non classés
            ).only("moyenne")

            if notes_unite.exists():
                self.moyenne_unite = round(
                    sum(item.moyenne for item in notes_unite) / notes_unite.count(), 2
                )
            else:
                self.moyenne_unite = 0

        super().save(*args, **kwargs)