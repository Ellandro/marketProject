from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Vente

@receiver(pre_save, sender=Vente)
def update_montant_total(sender, instance, **kwargs):
    if instance.produit and instance.quantite:
        prix_unitaire = instance.produit.prix
        montant_total = prix_unitaire * instance.quantite
        instance.montant_total = montant_total