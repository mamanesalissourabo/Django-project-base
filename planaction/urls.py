from django.urls import path
from . import views

urlpatterns = [
    path('', views.PlanActionListAndCreateView.as_view(), name='planaction-list'),
    path('planaction/<int:pk>/', views.PlanActionDetailView.as_view(), name='planaction-detail'),
    path('planaction/<int:pk>/delete/', views.PlanActionDeleteView.as_view(), name='planaction-delete'),
    path('create/', views.PlanActionCreateView.as_view(), name='planaction_create'),
]