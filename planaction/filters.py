# planaction/filters.py
import django_filters as df
from django import forms
from planaction.models import PlanAction, PlanActionStatuses
from base.models import User 
from incident.models import Incident

class PlanActionListFilter(df.FilterSet):
    reference = df.CharFilter(
        field_name='reference',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-solid',
            'placeholder': 'Rechercher par référence...'
        })
    )
    
    title = df.CharFilter(
        field_name='title',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-solid',
            'placeholder': 'Rechercher par titre...'
        })
    )
    
    status = df.ChoiceFilter(
        choices=PlanActionStatuses.choices,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-solid',
            'data-control': 'select2',
            'data-placeholder': 'Statut'
        })
    )
    
    created_by_user = df.ModelChoiceFilter(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-select form-select-solid',
            'data-control': 'select2',
            'data-placeholder': 'Tous les utilisateurs'
        })
    )
    
    incident = df.ModelChoiceFilter(
        queryset=Incident.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-select form-select-solid',
            'data-control': 'select2',
            'data-placeholder': 'Tous les incidents'
        })
    )

    class Meta:
        model = PlanAction
        fields = ['reference', 'title', 'status', 'created_by_user', 'incident']