from django.db import models

# Create your models here.
class Notification(models.Model):
    """Model definition for Notification."""
    titre = models.CharField(max_length=50)
    description = models.TextField()
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)


    # TODO: Define fields here

    class Meta:
        """Meta definition for Notification."""

        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created']

    def __str__(self):
        """Unicode representation of Notification."""
        return self.titre
