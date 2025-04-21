# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.incident_list, name='incident_list'),
    path('<int:pk>/', views.incident_detail, name='incident_detail'),
    path('<int:pk>/edit/', views.incident_update, name='incident_update'),
    path('create/', views.IncidentCreateView.as_view(), name='incident_create'),
    path('get_emplacements/', views.get_emplacements, name='get_emplacements'),
    # path('<int:pk>/delete/', views.incident_delete, name='incident_delete'),
]