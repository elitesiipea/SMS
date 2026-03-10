from django.db import models
from django.utils.translation import gettext_lazy as _


class CategorieProduit(models.Model):
    """Model definition for CategorieProduit."""
    etablissement = models.ForeignKey("gestion_academique.Etablissement", related_name="etablissement_categorie_produit", on_delete=models.CASCADE)
    nom = models.CharField(max_length=50)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    # TODO: Define fields here

    class Meta:
        """Meta definition for CategorieProduit."""

        verbose_name = 'Categorie Produit'
        verbose_name_plural = 'Categorie Produits'

    def __str__(self):
        """Unicode representation of CategorieProduit."""
        return self.nom
    
    @property
    def produits(self):
        return sum(item.quantite for item in self.categorie_produit.all())


class Produit(models.Model):
    """Model definition for Produit."""
    nom = models.CharField(max_length=150)
    image = models.FileField(upload_to='stocks/photo',null=True, blank=True)
    categorie = models.ForeignKey(CategorieProduit, related_name="categorie_produit", on_delete=models.CASCADE)
    quantite = models.IntegerField(default=0)
    quantite_minimal = models.IntegerField(default=0)
    localisation = models.CharField(max_length=150)
    description = models.TextField()
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    
    
    # TODO: Define fields here

    class Meta:
        """Meta definition for Produit."""

        verbose_name = 'Produit'
        verbose_name_plural = 'Produits'

    def __str__(self):
        """Unicode representation of Produit."""
        return self.nom

    def get_absolute_url(self):
        """Return absolute url for Produit."""
        return ('')

    # TODO: Define custom methods here

class Fournisseur(models.Model):
    """Model definition for Fournisseur."""
    etablissement = models.ForeignKey("gestion_academique.Etablissement", related_name="etablissement_fournisseurs", on_delete=models.CASCADE)
    nom = models.CharField(max_length=50)
    email = models.EmailField(max_length=254)
    contact = models.CharField(max_length=50)
    produits = models.ManyToManyField(CategorieProduit, verbose_name=_("Liste des produits fournis"))
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    # TODO: Define fields here

    class Meta:
        """Meta definition for Fournisseur."""

        verbose_name = 'Fournisseur'
        verbose_name_plural = 'Fournisseurs'

    def __str__(self):
        """Unicode representation of Fournisseur."""
        return self.nom


    def get_absolute_url(self):
        """Return absolute url for Fournisseur."""
        return ('')

    # TODO: Define custom methods here
    

class Commande(models.Model):
    """Model definition for Commandes."""
    fournisseur = models.ForeignKey(Fournisseur, related_name="commande_fournisseur", on_delete=models.CASCADE)
    bon_de_commande = models.FileField(upload_to='commandes/bon',null=True, blank=True)
    active = models.BooleanField(default=True)
    commande_recu = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    

    # TODO: Define fields here

    class Meta:
        """Meta definition for Commandes."""

        verbose_name = 'Commande'
        verbose_name_plural = 'Commandes'

    def __str__(self):
        """Unicode representation of Commandes."""
        return 'Commande N° {}-{}'.format(self.id, self.fournisseur)


    def get_absolute_url(self):
        """Return absolute url for Commandes."""
        return ('')

    # TODO: Define custom methods here

class ProduitCommande(models.Model):
    """Model definition for ProduitCommande."""
    commande = models.ForeignKey(Commande, related_name="produits_commandes", on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, related_name="commande_prod", on_delete=models.CASCADE)
    quantite = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    # TODO: Define fields here

    class Meta:
        """Meta definition for ProduitCommande."""

        verbose_name = 'Produit Commande'
        verbose_name_plural = 'ProduitCommandes'

    def __str__(self):
        """Unicode representation of ProduitCommande."""
        return 'Commande N°{}-{}-{}'.format(self.commande.id, self.produit.nom, self.quantite)


    # TODO: Define custom methods here

type_operation = (
    ('ENTREE DE PRODUIT' , 'ENTREE DE PRODUIT' ,),
    ('SORTIE DE PRODUIT' , 'SORTIE DE PRODUIT' ,),
    ('EMPRUNT DE PRODUIT', 'EMPRUNT DE PRODUIT',),
)
    
class Operation(models.Model):
    """Model definition for Operation."""
    etablissement = models.ForeignKey("gestion_academique.Etablissement", related_name="etablissement_operations", on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=type_operation)
    reference = models.CharField(max_length=150)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    returned = models.BooleanField(default=False)
    

    # TODO: Define fields here

    class Meta:
        """Meta definition for Operation."""

        verbose_name = 'Operation'
        verbose_name_plural = 'Operations'

    def __str__(self):
        """Unicode representation of Operation."""
        return '{}-{}'.format(self.type, self.reference)


    # TODO: Define custom methods here
    
class ProduitOperation(models.Model):
    """Model definition for ProduitOperation."""
    operation = models.ForeignKey(Operation, related_name="produits_operations", on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, related_name="operation_prod", on_delete=models.CASCADE)
    quantite = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    # TODO: Define fields here

    class Meta:
        """Meta definition for ProduitOperation."""

        verbose_name = 'Produit Operation'
        verbose_name_plural = 'Produit Operations'

    def __str__(self):
        """Unicode representation of ProduitOperation."""
        return '{}-{}-{}'.format(self.operation, self.produit, self.quantite)


    def get_absolute_url(self):
        """Return absolute url for ProduitOperation."""
        return ('')

    # TODO: Define custom methods here


