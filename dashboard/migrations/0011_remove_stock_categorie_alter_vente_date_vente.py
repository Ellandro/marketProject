# Generated by Django 5.0.3 on 2024-04-15 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0010_remove_produit_quantite_stock_categorie'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stock',
            name='categorie',
        ),
        migrations.AlterField(
            model_name='vente',
            name='date_vente',
            field=models.CharField(max_length=100),
        ),
    ]