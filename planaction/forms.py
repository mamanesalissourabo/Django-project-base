# planaction/forms.py
from django import forms
from planaction.models import PlanAction
from incident.models import Incident
from base.models import User

class PlanActionForm(forms.ModelForm):
    class Meta:
        model = PlanAction
        fields = ['title', 'description', 'incident', 'created_by_user']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control form-control-solid', 'placeholder': 'Titre du plan d\'action'}),
            'description': forms.Textarea(attrs={'class': 'form-control form-control-solid', 'placeholder': 'Description du plan d\'action', 'rows': 2}),
            'incident': forms.Select(attrs={'class': 'form-select form-control form-control-solid'}),
            'created_by_user': forms.Select(attrs={'class': 'form-select form-control form-control-solid', 'disabled': 'disabled'}),
        }
        labels = {
            'title': 'Titre',
            'description': 'Description',
            'incident': 'Incident associé',
            'created_by_user': 'Responsable de l\'action',
            }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Limite les choix à l'utilisateur connecté seulement
            self.fields['created_by_user'].queryset = User.objects.filter(pk=user.pk)
            # Pré-sélectionne l'utilisateur connecté
            self.initial['created_by_user'] = user.pk