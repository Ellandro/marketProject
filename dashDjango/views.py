from django.shortcuts import render
from django.http import HttpResponse
from django_plotly_dash import DjangoDash
from django.views.generic import TemplateView

class DashView(TemplateView):
    template_name = 'dash.html'
