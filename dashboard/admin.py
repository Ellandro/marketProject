
from django.contrib import admin
from .models import Produit, Commande, Categorie, Vente
from django.contrib.auth.models import Group
admin.site.site_header = 'Epsilon'
#admin.site.unregister(Group)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('nom','categorie', 'prix','expiration')
    list_filter = ('categorie',)

admin.site.register(Categorie)
admin.site.register(Produit, ProductAdmin)
admin.site.register(Commande)
admin.site.register(Vente)
