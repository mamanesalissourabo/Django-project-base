# urls.py
from django.urls import path
from . import views


urlpatterns = [
    path('', views.faq_list, name='faq_list'),
    path('accueil/', views.accueil, name='accueil'),
    path('support/', views.contact_support, name='contact_support'),
]