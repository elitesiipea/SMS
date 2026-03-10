from django.db import models
from PIL import Image
from io import BytesIO
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

class CategorieLivre(models.Model):
    """Model definition for CategorieLivre."""
    
    nom = models.CharField(max_length=50)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    # TODO: Define fields here

    class Meta:
        """Meta definition for CategorieLivre."""

        verbose_name = 'Categorie Livre'
        verbose_name_plural = 'Categorie Livres'

    def __str__(self):
        """Unicode representation of CategorieLivre."""
        return self.nom
    
    @property
    def livres(self):
        return self.livre_categorie.all()
    
    @property
    def nombre_livres(self):
        return self.livres.count()

    # TODO: Define custom methods here
    
class Livre(models.Model):
    
    """Model definition for Livre."""
    titre = models.CharField(max_length=120)
    categorie = models.ForeignKey(
        CategorieLivre, on_delete=models.CASCADE, related_name="livre_categorie"
    )
    auteur = models.CharField(max_length=120)
    image = models.ImageField(upload_to="bibliotheque/livre/images/", default="none.png")
    description = models.TextField()
    document = models.FileField(upload_to="bibliotheque/livre/document/", default="none.png")
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    # TODO: Define fields here

    class Meta:
        """Meta definition for Livre."""

        verbose_name = 'Livre'
        verbose_name_plural = 'Livres'
        ordering = ['titre']

    def __str__(self):
        """Unicode representation of Livre."""
        return self.titre

    def save(self):
        im = Image.open(self.image)
        output = BytesIO()
        im = im.resize((270, 320))
        im.save(output, format='PNG', quality=100)
        output.seek(0)
        self.image = InMemoryUploadedFile(output, 'ImageField', "%s.png" % self.image.name.split(
            '.')[0], 'image/png', sys.getsizeof(output), None)
        super(Livre, self).save()

    # TODO: Define custom methods here