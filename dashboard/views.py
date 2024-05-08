import datetime
import json
from datetime import timedelta
import plotly.graph_objs as go
import plotly.express as px
from django.template.loader import render_to_string
from reportlab.pdfgen import canvas
from io import BytesIO
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models.functions import ExtractMonth, ExtractYear
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from openpyxl import Workbook

from .models import Produit, Categorie, Commande, Vente, Stock
from .forms import ProduitForm, CategorieForm, VenteForm, SearchForm, StockForm, UploadFileForm, DataForm
from django.contrib.auth.models import User
from django.contrib import messages
import pandas as pd
from django.db.models import Sum, Count



def charts(request):


    sales_by_date = Vente.objects.annotate(
        month=ExtractMonth('date_vente'),
        year=ExtractYear('date_vente')
    ).values('year', 'month').annotate(
        total_sales=Count('id'),
    ).order_by('year', 'month')

    ventes = Vente.objects.annotate(
        mois=ExtractMonth('date_vente'),
        annee=ExtractYear('date_vente')
    ).values('mois', 'annee').annotate(
        chiffre_affaires=Sum('montant_total')
    ).order_by('annee', 'mois')
    years_months = [f"{sale['year']}-{sale['month']}" for sale in sales_by_date]
    total_sales = [sale['total_sales'] for sale in sales_by_date]
    total_chiffre_affaires = Vente.objects.aggregate(total_chiffre_affaires=Sum('montant_total'))[
        'total_chiffre_affaires']

    labels = [f"{vente['mois']}/{vente['annee']}" for vente in ventes]
    data = [vente['chiffre_affaires'] for vente in ventes]
    data = [float(vente['chiffre_affaires']) for vente in ventes]

    # Vente par par année
    ventes_par_annee = (
        Vente.objects
        .annotate(annee=ExtractYear('date_vente'))
        .values('annee')
        .annotate(nombre_ventes=Count('id'))
        .order_by('annee')
    )

    # Comparaison des ventes par année
    sales_data_2022 = get_sales_data_for_year(2022)
    sales_data_2023 = get_sales_data_for_year(2023)
    sales_data_2024 = get_sales_data_for_year(2024)

    Mois =['Janvier', 'Fevrier','Mars','Avril','Mai','Juin','Juillet','Août','Septembre','Octobre', 'Novembre','Decembre']
    fig_2022 = px.line(
        x=Mois,
        y=sales_data_2022,
        labels=Mois,
        title='Comparaison des ventes par année',
        template='plotly_dark',
        color_discrete_sequence=px.colors.qualitative.Plotly,
    )
    fig_2022.update_layout(
        height=600,  # Ajuster la hauteur du diagramme
    )


    fig_2022.add_trace(go.Scatter(x=Mois, y=sales_data_2022, name='vente 2022'))
    fig_2022.add_trace(go.Scatter(x=Mois, y=sales_data_2023, name='vente 2023'))
    fig_2022.add_trace(go.Scatter(x=Mois, y=sales_data_2024, name='vente 2024'))

    compare = fig_2022.to_html()
    diagram = px.pie(ventes_par_annee,
        values='nombre_ventes', names='annee', title='Nombre de vente par annee',
                     template='plotly_dark',
                     color_discrete_sequence=px.colors.qualitative.Plotly,
    )
    diagram.update_layout(

        height=600,  # Ajuster la hauteur du diagramme
    )


    fig = px.area(
        x= labels,
        y = total_sales,
        labels={'y':'Nombre de produit vendu', 'x':'Mois '},
        title='Chiffre d\'affaires par mois',
        template='plotly_dark',
        color_discrete_sequence=px.colors.qualitative.Plotly,
    )
    fig.update_layout(
        xaxis=dict(
            tickvals=labels,  # Utilisez les labels personnalisés comme valeurs de l'axe des x
            ticktext=labels,
            # Liste des étiquettes personnalisées
            tickfont=dict(
                size=14,  # Ajuster la taille des étiquettes de l'axe des x
            )
        ),
        yaxis=dict(
            tickfont=dict(
                size=14,  # Ajuster la taille des étiquettes de l'axe des y
            )
        ),
          # Ajuster la largeur du graphique
        height=600,  # Ajuster la hauteur du graphique
    )

    bar = go.Figure()

    # Ajout des courbes pour chaque année

    # Ajout des barres pour chaque année
    bar.add_trace(go.Bar(x=Mois, y=sales_data_2022, name='vente 2022', opacity=0.5))
    bar.add_trace(go.Bar(x=Mois, y=sales_data_2023, name='vente 2023', opacity=0.5))
    bar.add_trace(go.Bar(x=Mois, y=sales_data_2024, name='vente 2024', opacity=0.5))

    # Mise à jour de la mise en page
    bar.update_layout(
        xaxis_title='Mois',
        yaxis_title='Total des ventes',
        title='Comparaison des ventes par année',
        template='plotly_dark',
        height=600,  # Ajuster la hauteur du diagramme
        colorway=px.colors.qualitative.Plotly,
        barmode='group'  # Mode de regroupement des barres
    )
    graph = bar.to_html()
    diagram = diagram.to_html()
    charts = fig.to_html()
    context = {
        'charts':charts,
        'diagram':diagram,
        'compare':compare,
        'form':DataForm(),
        'graph':graph,
    }
    return render(request, 'Sales/chart.html', context)

def get_sales_data_for_year(year):
    sales_data = Vente.objects.filter(date_vente__year=year).annotate(
        month=ExtractMonth('date_vente')
    ).values('month').annotate(
        total_sales=Sum('quantite')
    ).order_by('month')

    sales_by_month = {month['month']: month['total_sales'] for month in sales_data}
    sales_for_year = [sales_by_month.get(month, 0) for month in range(1, 13)]

    return sales_for_year

@login_required(login_url='user-login')
def dashboard(request):
    """Render dashboard """
    orders = Commande.objects.all()
    products = Produit.objects.all()
    paginator = Paginator(products, 25)  # Affiche 25 ventes par page
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    sales_data_2022 = get_sales_data_for_year(2022)
    sales_data_2023 = get_sales_data_for_year(2023)
    sales_data_2024 = get_sales_data_for_year(2024)

    sales_data_2022_json = json.dumps(list(sales_data_2022))
    sales_data_2023_json = json.dumps(list(sales_data_2023))
    sales_data_2024_json = json.dumps(list(sales_data_2024))

    ventes_par_annee = (
        Vente.objects
        .annotate(annee=ExtractYear('date_vente'))
        .values('annee')
        .annotate(nombre_ventes=Count('id'))
        .order_by('annee')
    )
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
    ventes = Vente.objects.select_related('produit__categorie').order_by('-date_vente')  # Ordonner par date de vente (plus récente d'abord)

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
# Ajouter une vente ou plusieurs*

"""VenteFormSet = formset_factory(VenteForm, extra=1)
def add_sales(request):
    user = request.user.id
    # Récupérer l'utilisateur connecté
    utilisateur = get_object_or_404(User, id=request.user.id)

    #vendeur = get_object_or_404(User, IdUtilisateur=user)
    if request.method == 'POST':
        id_user = request.user.id
        vendeur = get_object_or_404(User, id=id_user)
        produit_formset = VenteFormSet(request.POST)
        print(produit_formset)
        if(produit_formset.is_valid):
            instances = produit_formset.save(commit=False)
            error_flag = False
            for instance in instances:
                produit = instance.IdProduit
                instance.montant_total = produit.prix * instance.quantite
            # date_et_heure = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            # instance.DateVente = timezone.now
                instance.IdVendeur_id = vendeur.id

            # Vérification de la quantité en stock
                produit_stock, _ = Stock.objects.get_or_create(produit=produit)
                if produit_stock.quantite < instance.quantite:
                    messages.warning(request,
                                     f"La quantité en stock ({produit_stock.quantite}) est insuffisante pour la vente.")
                    error_flag = True
                    continue

            # Vérifiez si la soustraction ne résulte pas en un nombre négatif
                if produit_stock.QuantiteStock - instance.QuantiteVendu < 0:
                    messages.warning(request, "La quantité en stock ne peut pas être négative après la vente.")
                    error_flag = True
                    continue

                instance.save()

        '''if not error_flag:
            return redirect('recu_vente', client_id=new_client.id)
            
        '''

    else:

        produit_formset = VenteFormSet()

    return render(request, 'Sales/add_sale.html',locals())"""

def montant_total_ventes_en_attente(ventes_en_attente):
    montant_total = sum(vente['montant_total'] for vente in ventes_en_attente)
    return montant_total

# Utilisez une liste pour stocker les ventes en attente
def save_sales(request, vente_data):
    print(vente_data)

    if request.method == 'POST':
        print(vente_data)
        # Enregistrez toutes les ventes en attente dans la base de données
        for vente_data in vente_data:
            vente = Vente.objects.create(
                produit=vente_data['produit'],
                personnel=request.user,
                quantite=vente_data['quantite'],
                montant_total=vente_data['montant_total']
            )
            vente.save()

        # Effacez la liste des ventes en attente dans la session
        vente_data = []


        messages.success(request, 'Les ventes ont été enregistrées avec succès.')


    # Si la méthode de la requête n'est pas POST, redirigez vers une autre vue par exemple


ventes_en_attente = []

def add_sales(request):
    # Assurez-vous que la liste des ventes en attente est initialisée dans la session de l'utilisateur


    if request.method == 'POST':
        form = VenteForm(request.POST)
        if form.is_valid():
            action = request.POST.get('action')
            if action == 'save_and_continue':
                print(action)
                produit = form.cleaned_data['produit']
                quantite = form.cleaned_data['quantite']

                stock = Stock.objects.get(produit=produit)
                if stock.quantite >= quantite:
                    prix_unitaire = produit.prix
                    montant_total = prix_unitaire * quantite

                    # Ajoutez la vente à la liste des ventes en attente dans la session
                    vente = {
                        'produit': produit,
                        'quantite': quantite,
                        'montant_total': montant_total
                    }
                    ventes_en_attente.append(vente)

                    messages.success(request, 'La vente a été ajoutée à la liste des ventes en attente.')
                    return redirect('dashboard:add_sale')
                else:
                    messages.error(request, 'La quantité demandée dépasse la quantité disponible en stock.')
            else:

                produit = form.cleaned_data['produit']
                quantite = form.cleaned_data['quantite']
                date_vente = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                stock = Stock.objects.get(produit=produit)
                if stock.quantite >= quantite:
                    prix_unitaire = produit.prix
                    montant_total = prix_unitaire * quantite
                    vente = {
                        'produit': produit,
                        'quantite': quantite,
                        'montant_total': montant_total,
                        'date_vente':date_vente
                    }
                    ventes_en_attente.append(vente)
                    montant_total_ventes = montant_total_ventes_en_attente(ventes_en_attente)
                    context={
                        'ventes': ventes_en_attente,
                        'total_amount':montant_total_ventes
                    }
                    save_sales(request, ventes_en_attente)
                    return render(request, 'Sales/receipt.html', context)

                else:
                    messages.error(request, 'La quantité demandée dépasse la quantité disponible en stock.')
        else:
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = VenteForm()

    context = {
        'form': form,
    }
    return render(request, 'Sales/ad_sale.html', context)

def generate_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="receipt.pdf"'

    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    # Convert HTML to PDF
    html = render_to_string('Sales/receipt.html')
    p.drawString(100, 750, html)
    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    return response




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
            produit_id = form.cleaned_data['produit'].id
            quantite = form.cleaned_data['quantite']
            print(produit_id)

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

'''
    Partie des grapiques pour le site
'''


def visuels(request):
    user = request.user

    # Convertir DateVente en DateField
    # Vente.objects.update(DateVente=Cast('DateVente', output_field=DateField()))

    # Récupérer l'utilisateur connecté
    utilisateur = get_object_or_404(User, id=request.user.id)

    # Utiliser la clé étrangère pour récupérer l'administrateur associé
   # administrateur = get_object_or_404(Adminitrateur, IdUtilisateur=utilisateur)
    # Meilleur produit vendu
    best_product = Vente.objects.values('produit__nom').annotate(total_sold=Sum('quantite')).order_by(
        '-total_sold')[:5]

    # Meilleur employé
    best_employee = Vente.objects.values('personnel__username').annotate(
        total_sales=Sum('montant_total')).order_by('-total_sales').first()

    # Top  des meilleurs categorie
    categories_mieux_vendues = Categorie.objects.values('nom').annotate(
        total_ventes=Sum('produit__vente__quantite')).order_by('-total_ventes')[:10]

    # Agrégation pour obtenir le nombre total de ventes par mois/année
    sales_by_date = Vente.objects.annotate(
        month=ExtractMonth('date_vente'),
        year=ExtractYear('date_vente')
    ).values('year', 'month').annotate(
        total_sales=Count('id'),
    ).order_by('year', 'month')

    ventes = Vente.objects.annotate(
        mois=ExtractMonth('date_vente'),
        annee=ExtractYear('date_vente')
    ).values('mois', 'annee').annotate(
        chiffre_affaires=Sum('montant_total')
    ).order_by('annee', 'mois')
    years_months = [f"{sale['year']}-{sale['month']}" for sale in sales_by_date]
    total_sales = [sale['total_sales'] for sale in sales_by_date]

    # Calculer le chiffre d'affaires total de toutes les ventes
    total_chiffre_affaires = Vente.objects.aggregate(total_chiffre_affaires=Sum('montant_total'))[
        'total_chiffre_affaires']

    labels = [f"{vente['mois']}/{vente['annee']}" for vente in ventes]

    data = [vente['chiffre_affaires'] for vente in ventes]
    data = [float(vente['chiffre_affaires']) for vente in ventes]

    Listeventes = Vente.objects.all().select_related('IdClient', 'IdProduit', 'IdProduit__IdCategorie', 'IdVendeur')
    nombre_total_ventes = Listeventes.count()

    #liste_client = client.objects.all()
   # nombre_total_client = liste_client.count()

    context = {
        'utilisateur': utilisateur,

        'best_product': best_product,
        'best_employee': best_employee,
        'total_chiffre_affaires': total_chiffre_affaires,
        'nombre_total_ventes': nombre_total_ventes,
        'categories_mieux_vendues': categories_mieux_vendues,
        'years_months': years_months,
        'total_sales': total_sales,
        'ventes': ventes,
        'labels': labels,
        'data': data,
    }
    return render(request, 'visuel.html', context)

def export_ventes_semaine_excel(request):
    # Déterminer la date de début de la semaine (lundi de cette semaine)
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())  # Lundi de cette semaine

    # Filtrer les ventes pour la semaine en cours
    ventes_semaine = Vente.objects.filter(date_vente__gte=start_of_week)

    if not ventes_semaine.exists():
        # Créer une réponse indiquant qu'il n'y a pas eu de vente cette semaine
        return render(request, 'vente_semaine.html')

    # Créer un nouveau classeur Excel
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = 'Ventes de la semaine'

    # Ajouter les en-têtes de colonne
    worksheet.append(['Produit', 'Quantité', 'Montant Total', 'Vendu par', 'Date de vente'])

    # Ajouter les données des ventes à la feuille Excel
    for vente in ventes_semaine:
        worksheet.append([
            vente.produit.nom,
            vente.quantite,
            vente.montant_total,
            vente.personnel.username,
            vente.date_vente.strftime('%d-%m-%Y')
        ])

    # Créer une réponse HTTP pour le fichier Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="ventes_semaine.xlsx"'

    # Écrire le contenu du classeur Excel dans la réponse HTTP
    workbook.save(response)

    return response