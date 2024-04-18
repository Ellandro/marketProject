from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Produit, Categorie, Commande, Vente, Stock
from .forms import ProduitForm, CategorieForm, VenteForm, SearchForm, StockForm, UploadFileForm
from django.contrib.auth.models import User
from django.contrib import messages
import pandas as pd
from django.db.models import Sum

@login_required(login_url='user-login')
def dashboard(request):
    """Render dashboard """
    orders = Commande.objects.all()
    products = Produit.objects.all()
    paginator = Paginator(products, 25)  # Affiche 25 ventes par page
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    if request.method =='POST':
        form = CategorieForm(request.POST)
    else:
        form = CategorieForm()

    return render(request, 'index.html', locals())


@login_required(login_url='user-login')
def produit(request):
    items = Produit.objects.all() # Using ORM
    stock =Stock.objects.all().select_related('produit')
    rows = Produit.objects.raw('SELECT * FROM dashboard_categorie')

    context = {
        'items': items,
        'rows':rows,
        'stock':stock
    }
    return render(request, 'products.html', context)

@login_required(login_url='user-login')
def add_product(request):
    if request.method == 'POST':
        form = ProduitForm(request.POST)
        if form.is_valid():
            # Extraire les données soumises
            product_name = form.cleaned_data.get('nom')
            product_category = form.cleaned_data.get('categorie')

            # Vérifier si un produit avec le même nom et la même catégorie existe déjà
            if Produit.objects.filter(nom=product_name, categorie=product_category).exists():
                messages.error(request, f'Un produit avec le nom "{product_name}" et la catégorie "{product_category}" existe déjà.')
            else:
                # Enregistrer le produit uniquement si aucun produit similaire n'existe
                form.save()
                messages.success(request, f'Le produit "{product_name}" a bien été enregistré.')
                return redirect('dashboard:product')
    else:
        form = ProduitForm()

    context = {
        'form': form,
    }
    return render(request, 'add-product.html', context)

def product_delete(request, pk):
    item = Produit.objects.get(id=pk)
    if request.method=='POST':
        item.delete()
        return redirect('dashboard:product')
    return render(request, 'product-delete.html')
def product_update(request,pk):
    item = Produit.objects.get(id=pk)
    if request.method=='POST':
        form = ProduitForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('dashboard:product')
    else:
        form = ProduitForm(instance=item)
    context = {
        'form':form,
    }
    return render(request,'edit-product.html', context)

def add_category(request):
    if request.method=='POST':
        form = CategorieForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard:product')
    else:
        form =CategorieForm()
    context = {
        'form':form
    }
    return render(request, 'Category/add-category.html', context)

def category_delete(request, pk):
    item = Categorie.objects.get(id=pk)
    if request.method=='POST':
        item.delete()
        return redirect('dashboard:product')
    return render(request, 'Category/delete-categorie.html')

def category_update(request, pk):
    item = Categorie.objects.get(id=pk)
    if request.method=='POST':
        form = CategorieForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('dashboard:product')
    else:
        form=CategorieForm(instance=item)
    context = {
        'form':form,
    }
    return render(request,'Category/edit-category.html', context)

@login_required(login_url='user-login')
def staff(request):
    workers = User.objects.all()
    context={
        'workers':workers
    }
    return render(request,'Users/staff.html', context)

def order(request):
    orders = Commande.objects.all()
    context={
        'orders':orders,
    }
    return render(request,'Commande/order.html', context)


def sales(request):
    search_form = SearchForm()
    ventes = Vente.objects.select_related('produit__categorie').all()
    nombre_total_ventes = ventes.count()

    if 'search_query' in request.GET:
        search_form = SearchForm(request.GET)
        if search_form.is_valid():
            search_query = search_form.cleaned_data['search_query']
            ventes = ventes.filter(produit__nom__icontains=search_query)

    paginator = Paginator(ventes, 15)  # Affiche 15 ventes par page
    page_number = request.GET.get('page')
    ventes = paginator.get_page(page_number)
    return render(request, 'Sales/vente.html',locals())

def add_sales(request):
    if request.method == 'POST':
        form = VenteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'La produit  a bien été enregistré')
            return redirect('dashboard:sale')
    else:
        form = VenteForm()
    context = {
        'form': form,
    }
    return render(request, 'Sales/add_sale.html', context)

def sale_delete(request, pk):
    item = Vente.objects.get(id=pk)
    if request.method=='POST':
        item.delete()
        return redirect('dashboard:sale')
    return render(request, 'Sales/delete-sale.html')

############################################# Gestion de stock ###########################################

def stock(request):
    stock = Stock.objects.all().select_related('produit')
    context={
       'stock':stock
    }
    return render(request, 'Stock/stock.html', context)


def save_stock(request, produit, quantite):
    if request.method == 'POST':
        try:
            # Vérifier si le produit appartient à la catégorie spécifiée
            from .models import Produit
            produit = Produit.objects.get(id=produit)

            # Vérifier s'il existe déjà une entrée de stock pour ce produit
            stock, created = Stock.objects.get_or_create(produit=produit)

            # Si le stock existe déjà, mettre à jour la quantité
            if not created:
                stock.quantite += quantite
            else:
                stock.quantite = quantite

            # Sauvegarder le stock mis à jour
            stock.save()

            return True, "Stock enregistré avec succès."

        except Produit.DoesNotExist:
            return False, "Le produit sélectionné n'appartient pas à la catégorie spécifiée."

        except Exception as e:
            return False, str(e)

def add_stock(request):
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            produit_id = form.cleaned_data['produit']
            quantite = form.cleaned_data['quantite']

            try:
                # Enregistrer le stock en utilisant la fonction save_stock
                result, message = save_stock(request, produit_id, quantite)
                if result:
                    messages.success(request, message)
                else:
                    messages.error(request, message)

            except Exception as e:
                messages.error(request, str(e))

    else:
        form = StockForm()

    return render(request, 'Stock/add_stock.html', {'form': form})


def update_stock(request,pk):
    item = Stock.objects.get(id=pk)
    if request.method == 'POST':
        form = StockForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('dashboard:stock')
    else:
        form = StockForm(instance=item)
    context = {
        'form': form,
    }
    return render(request, 'Stock/edit-stock.html', context)

def delete_stock(request, pk):
    item = Stock.objects.get(id=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('dashboard:stock')
    return render(request, 'Stock/delete-stock.html')
def handle_uploaded_file(file, user_id):
    # IdVendeur=request.user.id
    if file.name.endswith('.csv'):
        data = pd.read_csv(file, sep=";")
    elif file.name.endswith('.xlsx'):
        data = pd.read_excel(file)
    else:
        raise ValueError("Le fichier n'est pas un format supporté. Seuls CSV et Excel sont acceptés.")

    df = data.copy()
    for index, row in df.iterrows():
        vendeur_instance = User.objects.get(id=user_id)
        # Créer ou récupérer la catégorie de produit
        categorie, _ = Categorie.objects.get_or_create(nom=row['Type'])

        # Créer ou récupérer le produit
        produit, created_produit = Produit.objects.get_or_create(
            nom=row['Produit'],
            prix=row['Prix'],
            categorie=categorie
        )
        stock, created_stock = Stock.objects.get_or_create(
            produit=produit,
            quantite=250,
        )

        # Créer la vente si le produit, le client et la catégorie n'existent pas déjà

        Vente.objects.create(
            personnel=vendeur_instance,  # Vous devez définir l'ID du vendeur approprié
            produit=produit,
            quantite=1,  # Vous devez définir la quantité vendue appropriée
            montant_total=row['Prix'],
            date_vente=row['Date']
        )



def file(request):
    user = request.user.id
    vendeur = get_object_or_404(User, id=user)
    # form = UploadFileForm(request.POST, request.FILES)
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            if file.name.endswith('.csv'):
                # Traitement du fichier CSV avec Pandas
                handle_uploaded_file(file, vendeur.id)
                messages.success(request, "Vente enregistrée avec succès.")
                return render(request, 'file.html', {'form': form})

            elif file.name.endswith(('.xlsx', '.xls')):
                # Traitement du fichier Excel avec Pandas
                handle_uploaded_file(file, vendeur.id)
                messages.success(request, "Vente enregistrée avec succès.")
                return render(request, 'file.html', {'form': form})

            else:
                messages.warning(request, 'Le fichier doit être au format CSV ou excel')
    else:
        form = UploadFileForm()

    return render(request, 'file.html', {'form': form})