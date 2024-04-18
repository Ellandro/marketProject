# Generated by Django 5.0.3 on 2024-04-09 13:21

import dashboard.middleware
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0007_alter_commande_personnel_vente'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='vente',
            name='personnel',
            field=models.ForeignKey(default=dashboard.middleware.get_current_user, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]