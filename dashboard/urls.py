from django.urls import path
from . import views

app_name = 'dashboard'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('product/', views.produit, name='product'),
    path('file/', views.file, name='file'),
    path('product/delete/<int:pk>/', views.product_delete, name='product-delete'),
    path('product/update/<int:pk>/', views.product_update, name='product-update'),
    path('add-product', views.add_product, name='add_product'),
    ############################################### URL of Categorie #######################
    path('add-category',views.add_category, name='add-category'),
    path('cat_del/<int:pk>', views.category_delete, name='delete-categorie'),
    path('cat_update/<int:pk>', views.category_update, name='update-categorie'),
    path('staff/', views.staff, name='staff'),
    path('order/',views.  order, name='order'),
    ######### URL of Sale #####################
    path('sale/', views.sales, name='sale'),
    path('add_sale/', views.add_sales, name='add_sale'),
    path('sale/delete/<int:pk>', views.sale_delete, name='delete-sale'),

    path('stock/', views.stock, name='stock'),
    path('add_stock/', views.add_stock, name='add_stock'),
    path('stock/update/<int:pk>', views.update_stock, name='update_stock'),
    path('stock/delete/<int:pk>', views.delete_stock, name='delete_stock')

]