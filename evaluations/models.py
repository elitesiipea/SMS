from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse

session = (
    ('SESSION 1', 'SESSION 1',),
    ('SESSION 2', 'SESSION 2',)

)

# Create your models here.
class Note(models.Model):
    """Model definition for Note."""
    classe = models.ForeignKey('gestion_academique.Classe', related_name="classe_note", on_delete=models.CASCADE)
    matiere = models.ForeignKey('enseignant.ContratEnseignant', related_name="note_matiere", on_delete=models.CASCADE)
    use_note_1 = models.BooleanField(
        default=True, help_text="Cocher si la note 1 est prise en compte")
    use_note_2 = models.BooleanField(
        default=True, help_text="Cocher si la note 2 est prise en compte")
    use_note_3 = models.BooleanField(
        default=True, help_text="Cocher si la note 3 est prise en compte")
    use_note_partiel = models.BooleanField(
        default=True, help_text="Cocher si la note du partiel est prise en compte")
    partiel_uniquement = models.BooleanField(
        default=False, help_text="Cocher si uniquement la note du partiel est prise en compte")
    fichier = models.FileField(upload_to='notes/fichiers/')
    coefficient_note_partiel = models.IntegerField(default=1)
    coeeficient_matiere = models.IntegerField(default=1)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)


    # TODO: Define fields here

    class Meta:
        """Meta definition for Note."""

        verbose_name = 'Note'
        verbose_name_plural = 'Notes'

    def __str__(self):
        """Unicode representation of Note."""
        return f'{self.classe} {self.matiere}'

    def save(self, *args, **kwargs):
        """Save method for Note."""
        # Check if there is an existing instance with the same class and subject
        existing_instance = Note.objects.filter(classe=self.classe, matiere=self.matiere).first()
        if existing_instance and existing_instance.pk != self.pk:
            pass
        else:
            self.coeeficient_matiere = self.matiere.matiere.coefficient
            if self.classe.classe_universitaire:
                self.coefficient_note_partiel = 2
            super().save(*args, **kwargs)
            
            

    def url(self):
        """Return absolute url for Note."""
        return reverse('evaluation_details', kwargs={'classe_id' : self.classe.id , 'pk' : self.pk })

    # TODO: Define custom methods here


class Resultat(models.Model):
    """Model definition for Resultat."""
    note = models.ForeignKey(
        Note, related_name="note_resultat", on_delete=models.CASCADE
    )
    etudiant = models.ForeignKey(
        "inscription.Inscription", related_name="insription_note", on_delete=models.CASCADE
    )
    note_1 = models.FloatField(default=0, validators=[
                               MaxValueValidator(20), MinValueValidator(0)])
    note_2 = models.FloatField(default=0, validators=[
                               MaxValueValidator(20), MinValueValidator(0)])
    note_3 = models.FloatField(default=0, validators=[
                               MaxValueValidator(20), MinValueValidator(0)])
    note_partiel = models.FloatField(
        default=0, validators=[MaxValueValidator(20), MinValueValidator(0)])
    non_classe = models.BooleanField(
        default=False, help_text="Cocher si l'etudiant est non classé dans la matiere")
    session = models.CharField(
        max_length=10, choices=session, default="SESSION 1")
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    moyenne = models.FloatField(default=0, editable=False)
    moyenne_coefficient = models.FloatField(default=0, editable=False)
    
    def calculer_moyenne(self):
        if self.note.classe.classe_universitaire:
            total_notes = sum([
                self.note_1 * self.note.use_note_1,
                self.note_2 * self.note.use_note_2,
                self.note_3 * self.note.use_note_3
            ])
            moyenne_notes = total_notes / (self.note.use_note_1 + self.note.use_note_2 + self.note.use_note_3)
            
            if self.note.partiel_uniquement:
                return self.note_partiel
            else:
                return round(((moyenne_notes * 40) + (self.note_partiel * 60)) / 100, 2)
        else:
            count_used_notes = sum([
                self.note.use_note_1,
                self.note.use_note_2,
                self.note.use_note_3,
                self.note.use_note_partiel
            ])
            
            total_score = sum([
                self.note_1 * self.note.use_note_1,
                self.note_2 * self.note.use_note_2,
                self.note_3 * self.note.use_note_3,
                self.note_partiel * self.note.use_note_partiel
            ])
            
            return round(total_score / count_used_notes, 2) if count_used_notes > 0 else 0

    def calculer_moyenne_coefficient(self):
        return self.calculer_moyenne() * self.note.coeeficient_matiere

    def save(self, *args, **kwargs):
        self.moyenne = self.calculer_moyenne()
        self.moyenne_coefficient = round(self.calculer_moyenne_coefficient(),2)
        super().save(*args, **kwargs)
        
    @property
    def moyenne_unite(self):
        notes = Resultat.objects.filter(
            etudiant=self.etudiant, 
            note__matiere__matiere__unite=self.note.matiere.matiere.unite
            )
        return round((sum(item.moyenne for item in notes)) / notes.count(),2)