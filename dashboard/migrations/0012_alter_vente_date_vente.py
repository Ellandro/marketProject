# Generated by Django 5.0.3 on 2024-04-15 20:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0011_remove_stock_categorie_alter_vente_date_vente'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vente',
            name='date_vente',
            field=models.DateField(auto_now_add=True, null=True),
        ),
    ]
