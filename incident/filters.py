import django_filters as df
from django import forms
from incident.models import Incident, IncidentStatuses
from base.models import User 

class IncidentListFilter(df.FilterSet):
    reference = df.CharFilter(
        field_name='reference',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-solid',
            'placeholder': 'Rechercher par référence...'
        })
    )
    
    name = df.CharFilter(
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-solid',
            'placeholder': 'Rechercher par nom...'
        })
    )

    type_incident = df.ChoiceFilter(
    field_name='type_incident',
    choices=[
        ('PA', 'Presque-Accident'),
        ('OSE', 'Observation Sécurité/Environnement'),
    ],
    widget=forms.Select(attrs={
        'class': 'form-select form-select-solid',
        'data-control': 'select2',
        'data-placeholder': "Type d'incident"
    }),
    label="Type d'incident"
    )

    status = df.ChoiceFilter(
        choices=IncidentStatuses.choices,  
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
    
    report_date = df.DateFromToRangeFilter(
        widget=df.widgets.RangeWidget(attrs={
            'class': 'form-control form-control-solid',
            'type': 'date'
        })
    )

    class Meta:
        model = Incident
        fields = ['reference', 'name', 'type_incident', 'status', 'created_by_user', 'report_date']