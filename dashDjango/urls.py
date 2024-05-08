from django.urls import path
from . import views
app_name = 'dashDjango'
urlpatterns = [
    path('dash/', views.dash_integration_view, name='dash_integration'),
]