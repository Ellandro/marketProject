# Generated by Django 5.0.3 on 2024-03-26 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0004_categorie_alter_commande_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='produit',
            name='expiration',
            field=models.DateField(default='2024-12-31'),
        ),
    ]
