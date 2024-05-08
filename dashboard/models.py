from django.db import models
from django.contrib.auth.models import User
from .middleware import get_current_user


class Categorie(models.Model):
    nom = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural='Categories'

    def __str__(self):
        return f'{self.nom}'
class Produit(models.Model):
    nom = models.CharField(max_length=100, null=True)
    categorie = models.ForeignKey(Categorie, models.CASCADE, null=True)
    prix = models.PositiveIntegerField(default=0)
    expiration = models.DateField(default='2024-12-31')

    class Meta:
        verbose_name_plural = 'Produits'

    def __str__(self):
        return f'{self.nom}'

class Commande(models.Model):
    produit = models.ForeignKey(Produit,on_delete=models.CASCADE, null=True)
    personnel = models.ForeignKey(User,models.CASCADE, null=True, default=get_current_user)
    quantite = models.PositiveIntegerField(null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Commande'

    def __str__(self):
        return f'{self.produit} commandé par {self.personnel.username}'

class Vente(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, null=True)
    personnel = models.ForeignKey(User, on_delete=models.CASCADE, null=True, default=get_current_user)
    quantite = models.PositiveIntegerField(null=True)
    montant_total = models.PositiveIntegerField(default=0)
    date_vente = models.DateField(null=True, auto_now_add=True)

    class Meta:
        ordering = ('date_vente',)
        verbose_name_plural = 'Ventes'

    def __str__(self):
        return f'{self.quantite} de {self.produit.nom} vendu par {self.personnel.username} le {self.date_vente}'

    def save(self, *args, **kwargs):
        if self.produit and self.quantite:
            self.montant_total = self.produit.prix * self.quantite
        super(Vente, self).save(*args, **kwargs)

class Stock(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, null=True)
    #categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE,null=True)
    quantite = models.PositiveIntegerField(null=True)
    date = models.DateField(auto_now_add=True)

class Receipt(models.Model):
    vente = models.ForeignKey(Vente, on_delete=models.CASCADE)
    personnel = models.ForeignKey(User, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)
    contenu = models.TextField()

    def __str__(self):
        return f"Reçu pour la vente {self.vente.id} par {self.personnel.username}"