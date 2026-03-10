from django.db import models
from django.utils import timezone
from datetime import timedelta
from gestion_academique.models import Etablissement
from django.urls import reverse
class Car(models.Model):
    etablissement = models.ForeignKey(Etablissement, on_delete=models.CASCADE, related_name="car_etablissement")
    marque = models.CharField(max_length=50)
    immatriculation = models.CharField(max_length=155, unique=True)
    nombre_places = models.PositiveIntegerField()
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.immatriculation

class Trajet(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="car_trajet")
    depart = models.CharField(max_length=100)
    arrive = models.CharField(max_length=100)
    cout_mensuel = models.IntegerField()
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.depart} - {self.arrive}"
    
    @property
    def abonnements(self):
        return self.trajet_abonnements.all()
    
    @property
    def abonnements_count(self):
        return self.abonnements.count()

class Abonnement(models.Model):
    etudiant = models.ForeignKey("etudiants.Etudiant", on_delete=models.CASCADE, related_name="etudiant_trajet")
    trajet = models.ForeignKey(Trajet, on_delete=models.CASCADE, related_name="trajet_abonnements")
    from_date = models.DateField(default=timezone.now)
    to_date = models.DateField(default=timezone.now)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    
    ###################"
    # Lorem

    def __str__(self):
        return f"{self.etudiant} - {self.trajet.depart} to {self.trajet.arrive}"
    
    @property
    def est_date_passee(self):
        # Obtenez la date actuelle
        date_actuelle = timezone.now().date()

        # Comparez la date stockée dans to_date avec la date actuelle
        return self.to_date < date_actuelle


class Paiement(models.Model):
    """Model definition for Paiement."""
    abonnement         = models.ForeignKey(Abonnement, related_name="abonnement_paiement",  on_delete=models.CASCADE)
    montant = models.FloatField(default=0)
    source = models.CharField(max_length=150, blank=True, null=True)
    reference = models.CharField(max_length=150, blank=True, null=True)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    ############Pour Api
    confirmed = models.BooleanField(default=False)
    wave_launch_url = models.CharField(max_length=250, null=True, blank=True)
    wave_id = models.CharField(max_length=250, null=True, blank=True)

    # TODO: Define fields here

    class Meta:
        """Meta definition for Paiement."""

        verbose_name = 'Paiement'
        verbose_name_plural = 'Paiements'

    def __str__(self):
        """Unicode representation of Paiement."""
        return f'{self.abonnement} - {self.montant}'

    def save(self,*args, **kwargs):
        """Save method for Paiement."""
        if self.confirmed:
            # Update the paye field of the related Inscription
            self.abonnement.to_date += timedelta(days=31)
            self.abonnement.save()
            # Save the Paiement instance
            super(Paiement, self).save(*args, **kwargs)
        else:
            super(Paiement, self).save(*args, **kwargs)

    @property
    def success_url(self):
        return reverse('wavesuccessCar', kwargs={'pk': self.pk}) 

    @property
    def error_url(self):
        return reverse('waveerrorCar', kwargs={'pk': self.pk}) 
    
    # TODO: Define custom methods here