from django import forms
from .models import Produit, Categorie, Commande, Vente, Stock


class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['nom','categorie',  'prix', 'expiration']

class CategorieForm(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = ['nom',]

class CommandeForm(forms.ModelForm):
    class Meta:
        model = Commande
        fields = ['produit','quantite']

"""class VenteForm(forms.ModelForm):
    class Meta:
        model = Vente
        exclude = ['personnel', 'montant_total']
"""


class VenteForm(forms.ModelForm):
    class Meta:
        model = Vente
        exclude = ['personnel', 'montant_total']
class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['produit','quantite']

class UploadFileForm(forms.Form):
    file = forms.FileField(label='Charger un fichier de vente', widget=forms.FileInput(
            attrs= {'class':'form-control li'}),
            error_messages={'required':''})

class SearchForm(forms.Form):
    search_query = forms.CharField(label='Recherche', max_length=100)
class DataForm(forms.Form):
    start = forms.DateTimeField(widget=forms.DateInput(attrs={'type':'date'}))
    end = forms.DateTimeField(widget=forms.DateInput(attrs={'type':'date'}))