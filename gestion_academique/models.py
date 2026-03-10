from django.db import models
from cloudinary.models import CloudinaryField
from django.contrib import messages
from django.urls import reverse
from emplois_du_temps.models import EmploisDutemps
import secrets
import sys
import string
from django.shortcuts import get_object_or_404
from datetime import timedelta
from django.utils.timezone import now
import numpy as np


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
    """
    Modèle représentant un établissement scolaire.

    Champs principaux :
    - nom : Nom usuel de l'établissement (ex. "Université XYZ").
    - sigle : Sigle ou abréviation (ex. "UXYZ").
    - code : Code interne ou officiel.
    - full_name : Dénomination complète de l'établissement.
    - logo : Logo de l'établissement.
    - cachet_scolarite : Cachet utilisé pour les documents de scolarité.
    - footer_bull : Texte de pied de page pour les bulletins / documents.
    - contact : Numéro de téléphone principal.
    - email : Adresse email principale.
    - site : Site web (URL).
    - active : Indique si l'établissement est actif.
    - is_college : Indique s'il s'agit d'un collège (vs supérieur).
    - wave_api_key : Clé API Wave pour les paiements (optionnel).
    - created : Date de création.
    - date_update : Date de dernière mise à jour.
    """

    nom = models.CharField(max_length=150)
    sigle = models.CharField(max_length=150)
    code = models.CharField(max_length=150)
    full_name = models.TextField()
    logo = models.FileField(
        upload_to='etablissement/logo',
        null=True,
        blank=True,
        help_text="Logo officiel de l'établissement."
    )
    cachet_scolarite = models.FileField(
        upload_to='etablissement/cachet_scolarite',
        null=True,
        blank=True,
        help_text="Cachet utilisé pour les documents de scolarité."
    )
    footer_bull = models.TextField(
        help_text="Texte de pied de page pour les bulletins et relevés."
    )
    contact = models.CharField(
        max_length=254,
        help_text="Numéro de téléphone principal de l'établissement."
    )
    email = models.EmailField(
        max_length=254,
        help_text="Adresse email principale (ex. contact@ecole.ci)."
    )
    # Mieux en URLField qu'EmailField
    site = models.URLField(
        max_length=254,
        help_text="Adresse du site web (ex. https://www.ecole.ci)."
    )
    active = models.BooleanField(default=True)
    is_college = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    wave_api_key = models.TextField(
        null=True,
        blank=True,
        help_text="Clé API Wave pour les paiements (optionnel)."
    )

    class Meta:
        verbose_name = "Etablissement"
        verbose_name_plural = "Etablissements"
        ordering = ["-created"]

    def __str__(self):
        """Représentation textuelle de l'établissement."""
        return self.full_name or self.nom

    @property
    def salles_count(self):
        """
        Retourne le total des places de toutes les salles
        via les campus rattachés (si tu as un related_name='campus').
        """
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
    closed = models.BooleanField(default=False)
    date_update = models.DateTimeField(auto_now=True)
    # TODO: Define fields here

    class Meta:
        """Meta definition for Classe."""

        verbose_name = 'Classe'
        verbose_name_plural = 'Classes'
        ordering = ['niveau', 'nom']
        
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
    
    @property
    def matieres(self):
        try:
            # Rechercher la maquette correspondante
            maquette = Maquette.objects.filter(
                annee_academique=self.annee_academique,
                filiere=self.filiere,
                niveau=self.niveau,
                maquette_universitaire=self.classe_universitaire,
                maquette_professionnel_jour=self.classe_professionnelle_jour,
                maquette_professionnel_soir=self.classe_professionnelle_soir,
                maquette_cours_en_ligne=self.classe_online
            ).first()

            # Vérifier si une maquette a été trouvée
            if maquette:
                return maquette.matieres.all()
            else:
                return []
        except Maquette.DoesNotExist:
            # Si aucune maquette n'est trouvée, retourner une liste vide
            return []


    @property
    def volumes_S1(self):
        # Calculer les volumes seulement si des matières existent
        if not self.matieres:
            return 0
        return sum(item.volume_total for item in self.matieres.filter(unite__semestre__exact="SEMESTRE 1"))

    @property
    def volumes_S2(self):
        # Calculer les volumes seulement si des matières existent
        if not self.matieres:
            return 0
        return sum(item.volume_total for item in self.matieres.filter(unite__semestre__exact="SEMESTRE 2"))

    @property
    def rea_volumes_S1(self):
        # Calculer le volume réalisé pour le semestre 1 seulement s'il y a des progressions
        if not self.progression_matiere_classe.exists():
            return 0
        return sum(item.volume_realise for item in self.progression_matiere_classe.filter(matiere__unite__semestre__exact="SEMESTRE 1"))

    @property
    def rea_volumes_S2(self):
        # Calculer le volume réalisé pour le semestre 2 seulement s'il y a des progressions
        if not self.progression_matiere_classe.exists():
            return 0
        return sum(item.volume_realise for item in self.progression_matiere_classe.filter(matiere__unite__semestre__exact="SEMESTRE 2"))

    @property
    def progres_S1(self):
        # Calculer le pourcentage de progression seulement si volumes_S1 est non nul
        if self.volumes_S1 == 0:
            return 0
        return round((self.rea_volumes_S1 * 100) / self.volumes_S1)

    @property
    def progres_S2(self):
        # Calculer le pourcentage de progression seulement si volumes_S2 est non nul
        if self.volumes_S2 == 0:
            return 0
        return round((self.rea_volumes_S2 * 100) / self.volumes_S2)

    @property
    def progres_total(self):
        # Calculer le pourcentage total seulement si les progressions des semestres sont disponibles
        if self.progres_S1 == 0 and self.progres_S2 == 0:
            return 0
        return round((self.progres_S1 + self.progres_S2) / 2)

    




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
                existing_classes = Classe.objects.filter(
                    filiere=filiere, 
                    niveau=niveau,
                    classe_universitaire=self.classe_universitaire,
                    classe_professionnelle_jour=self.classe_professionnelle_jour,
                    classe_professionnelle_soir=self.classe_professionnelle_soir,
                    classe_online=self.classe_online
                    ).values_list('nom', flat=True)
                
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
        return self.matiere_ue.all().order_by('unite__semestre','nom')

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
    
    @property
    def cout_total(self):
        return self.cout + self.cout_td
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
    

from datetime import datetime
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
        #ordering = ['diplome','nom','prenom']

    @property
    def email(self):
        """
        Génère une adresse email au format `prenom-nom@iipea.com`.
        Les espaces et apostrophes sont retirés.
        """
        # Nettoyer le prénom et le nom
        prenom_cleaned = ''.join(char for char in self.prenom.split()[0] if char.isalnum())
        nom_cleaned = ''.join(char for char in self.nom if char.isalnum())
        # Générer l'email
        return f"{prenom_cleaned.lower()}-{nom_cleaned.lower()}@iipea.com"

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

    @property
    def date_soutenance_formatted(self) -> str:
        """
        Retourne `date_soutenance` au format 'JJ/MM/AAAA'.
        Si la chaîne ne matche pas, renvoie la valeur brute.
        """
        if not self.date_soutenance:
            return ""
        for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
            try:
                dt = datetime.strptime(self.date_soutenance, fmt)
                return dt.strftime('%d/%m/%Y')
            except ValueError:
                continue
        # Si aucun parsing n’a marché, on renvoie la chaîne d’origine
        return self.date_soutenance

    # TODO: Define custom methods here
################################################ modele pour les progressions 



class ClasseProgression(models.Model):
    """Model definition for ClasseProgression."""
    classe = models.ForeignKey(Classe, related_name="progression_matiere_classe", on_delete=models.CASCADE)
    matiere = models.ForeignKey(Matiere, related_name="matiere_classe_progress", on_delete=models.CASCADE)
    enseignant = models.CharField(max_length=50)
    support = models.FileField(upload_to='enseignant/support',null=True, blank=True)
    syllabys = models.FileField(upload_to='enseignant/syllabus',null=True, blank=True)
    piece = models.FileField(upload_to='enseignant/piece',null=True, blank=True)
    rib = models.FileField(upload_to='enseignant/rib',null=True, blank=True)
    active = models.BooleanField(default=True)
    cours_en_tronc_commun = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    volume_realise = models.IntegerField(default=0)
    note_deposee = models.BooleanField(default=False)
    paiement_effectue = models.BooleanField(default=False)
    demande_de_paiement_initie = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    # TODO: Define fields here

    class Meta:
        """Meta definition for ClasseProgression."""

        verbose_name = 'Classe Progression'
        verbose_name_plural = 'Classe Progressions'

    def __str__(self):
        """Unicode representation of ClasseProgression."""
        return "{} {} {} ".format(self.classe, self.matiere, self.enseignant)
    
    def cours_url(self):
        return reverse('course_details_2', kwargs={'pk' : self.pk })
    
    @property
    def reste(self):
        return self.matiere.volume_total - self.volume_realise
    
    @property
    def progress(self):
        return round((self.volume_realise * 100)/ self.matiere.volume_total)
    
    @property
    def is_close(self):
        if self.volume_realise == self.matiere.volume_total:
            return True 
        return False
    
    @property
    def price(self):
        return self.matiere.cout_total
    
    @property
    def color(self):
        progress = self.progress
        if progress <= 20:
            return "red"            # 0-20%: Rouge (peu de progression)
        elif 20 < progress <= 40:
            return "orange"         # 21-40%: Orange
        elif 40 < progress <= 60:
            return "yellow"         # 41-60%: Jaune (progression modérée)
        elif 60 < progress <= 80:
            return "lightgreen"     # 61-80%: Vert clair (bonne progression)
        elif 80 < progress < 100:
            return "lightblue"          # 81-99%: Vert
        else:
            return "green"           # 100%: Bleu (progression complète)
    
    @property
    def pointages_first(self):
        try:
            return self.progression_matiere.earliest('created')
        except self.progression_matiere.model.DoesNotExist:
            return None

    @property
    def pointages_last(self):
        try:
            return self.progression_matiere.latest('created')
        except self.progression_matiere.model.DoesNotExist:
            return None


    @property
    def lock_date(self):
        """Calcule la date à laquelle le cours sera verrouillé."""
        first_pointage = self.pointages_first
        if not first_pointage:
            return None  # Si aucun pointage, il n'y a pas de date de verrouillage.

        # Calcul du nombre de jours ouvrés nécessaires pour terminer le cours
        total_hours = self.matiere.volume_total
        days_needed = np.ceil(total_hours / 2)  # 2 heures par jour ouvrable

        # Ajouter uniquement les jours ouvrés (lundi-vendredi)
        end_date = first_pointage.created
        while days_needed > 0:
            end_date += timedelta(days=1)
            if end_date.weekday() < 5:  # 0=Lundi, 4=Vendredi
                days_needed -= 1

        # Ajouter les deux semaines après la fin du cours
        lock_date = end_date + timedelta(weeks=2)

        return lock_date.date()  # Conversion en date pour éviter les erreurs

    @property
    def is_locked(self):
        """Vérifie si le cours est verrouillé."""
        if not self.lock_date:
            return False  # Si aucune date de verrouillage, le cours n'est pas verrouillé.

        return now().date() >= self.lock_date  # Comparaison correcte entre deux dates




class Pointage(models.Model):
    matiere = models.ForeignKey(ClasseProgression, related_name="progression_matiere", on_delete=models.CASCADE)
    volume_realise = models.CharField(max_length=50)
    observation = models.TextField()
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    code = models.CharField(max_length=10, null=True, blank=True)
    """Model definition for Pointage."""

    # TODO: Define fields here

    class Meta:
        """Meta definition for Pointage."""

        verbose_name = 'Pointage'
        verbose_name_plural = 'Pointages'

    def __str__(self):
        """Unicode representation of Pointage."""
        return "{} {}".format(self.matiere, self.volume_realise)



    def get_absolute_url(self):
        """Return absolute url for Pointage."""
        return ('')

    # TODO: Define custom methods here



class DossierMinistere(models.Model):
    """Model definition for DossierMinistere."""
    matricule_etudiant = models.CharField(max_length=14, unique=True)
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    date_de_naissance =  models.DateField(auto_now=False, auto_now_add=False)
    filiere = models.ForeignKey(Filiere, related_name="dossiers_filiere", on_delete=models.CASCADE)
    extrait_de_naissance = models.FileField(upload_to="ministere/dossiers/extraits/", max_length=100)
    justificatif_d_identite = models.FileField(upload_to="ministere/dossiers/pieces/", max_length=100)
    collante_du_bac = models.FileField(upload_to="ministere/dossiers/bacs", max_length=100)
    telephone = models.CharField(max_length=50)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    # TODO: Define fields here

    class Meta:
        """Meta definition for DossierMinistere."""

        verbose_name = 'DossierMinistere'
        verbose_name_plural = 'DossierMinisteres'

    def __str__(self):
        """Unicode representation of DossierMinistere."""
        return "{} {}".format(self.nom, self.nom)


    def get_absolute_url(self):
        """Return absolute url for DossierMinistere."""
        return ('')

    # TODO: Define custom methods here

###############################################################################
# Generer les recus de paiement

from django.db import models
from django.utils.crypto import get_random_string
from django.utils.timezone import now
import pandas as pd
import datetime
from workalendar.europe import France  # Modifier selon le pays


# Fonction pour générer un code unique de 10 caractères
def generate_unique_code():
    return get_random_string(10, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')

# Fonction pour obtenir une date de création valide (jour ouvrable)
def get_valid_creation_date():
    cal = France()  # Modifier selon ton pays
    start_date = datetime.date(2024, 9, 1)
    end_date = datetime.date(2025, 3, 2)
    valid_dates = [
        d for d in pd.date_range(start=start_date, end=end_date).to_pydatetime()
        if cal.is_working_day(d.date())
    ]
    return valid_dates[0].date() if valid_dates else now().date()

import random
from datetime import datetime, timedelta

# Fonction pour générer une date au format demandé
def generate_business_day():
    # Plage de dates entre le 1er septembre 2024 et le 28 février 2025
    start_date = datetime(2024, 9, 1)
    end_date = datetime(2025, 2, 28)

    # Liste pour stocker les jours ouvrables
    business_days = []

    # Boucle pour générer tous les jours ouvrables dans la plage donnée
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() < 5:  # Du lundi (0) au vendredi (4)
            business_days.append(current_date)
        current_date += timedelta(days=1)

    # Choisir une date aléatoire parmi les jours ouvrables
    random_day = random.choice(business_days)

    # Format de la date souhaité "Lundi 04 Janvier 2025 à 08:16"
    return random_day.strftime("%d/%m/%Y")



# Modèle pour stocker les données importées
class Student(models.Model):
    ident_perm = models.CharField(max_length=150, unique=True)
    nom = models.CharField(max_length=150)
    prenom = models.CharField(max_length=150)
    date_naissance = models.DateField()
    lieu_naissance = models.CharField(max_length=150)
    filiere = models.CharField(max_length=150)
    niveau = models.CharField(max_length=150)
    classe = models.CharField(max_length=150)
    elite_id = models.CharField(max_length=150, blank=True, null=True)
    status = models.CharField(max_length=150)
    sexe = models.CharField(max_length=150)
    contact = models.CharField(max_length=150, blank=True, null=True)
    photo = models.TextField()
    etablissement = models.CharField(max_length=150)
    code_unique = models.CharField(max_length=150, default=generate_unique_code, unique=True)
    email = models.EmailField(unique=False)
    created = models.DateTimeField(auto_now_add=True)




    def save(self, *args, **kwargs):
        # Générer l'email sans caractères spéciaux
        prenom_clean = ''.join(c for c in self.prenom.split()[0] if c.isalnum())
        self.email = f"{self.nom.lower()}-{prenom_clean.lower()}@iipea.com"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nom} {self.prenom}"

    @property
    def date_si(self):
        return generate_business_day()
