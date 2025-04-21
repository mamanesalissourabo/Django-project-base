from django import forms
from incident.models import Incident
from base.models import Emplacement, Site, User
from django.utils.translation import gettext_lazy as _

class IncidentForm(forms.ModelForm):
    type_incident = forms.ChoiceField(
        choices=[
            ('', '---------'),
            ('PA', _('Presque-Accident')),
            ('OSE', _('Observation Sécurité/Environnement')),
        ],
        label=_("Type d'incident"),
        widget=forms.Select(attrs={'class': 'form-select form-control form-control-solid'}),
        required=True
    )
                  
    consequence_ose = forms.CharField(
        required=False,
        label=_("Quelle en serait la conséquence ?"),
        widget=forms.Textarea(attrs={'class': 'form-control form-control-solid', 'rows': 2})
    )
    
    solution_ose = forms.CharField(
        required=False,
        label=_("Quelle est la solution à votre avis ?"),
        widget=forms.Textarea(attrs={'class': 'form-control form-control-solid', 'rows': 2})
    )
    
    action_correction = forms.NullBooleanField(
        required=False,
        label=_("Action de correction immédiate ?"),
        widget=forms.Select(
            attrs={'class': 'form-control form-control-solid'},
            choices=[_(None, '---------'), 
                     _(True, 'Oui'), 
                     _(False, 'Non')]
        )
    )
    
    photo_correction = forms.ImageField(
        required=False,
        label=_("Photo de la correction"),
        widget=forms.ClearableFileInput(attrs={'class': 'form-control form-control-solid'})
    )
    
    commentaire_correction = forms.CharField(
        required=False,
        label=_("Commentaire sur la correction"),
        widget=forms.Textarea(attrs={'class': 'form-control form-control-solid', 'rows': 2})
    )

    blessure_potentielle = forms.NullBooleanField(
        required=False,
        label=_("Blessure potentielle ?"),
        widget=forms.Select(
            attrs={'class': 'form-control form-control-solid'},
            choices=[(None, '---------'), 
                     (True, 'Oui'), 
                     (False, 'Non')]
        )
    )
    
    cause_principale = forms.CharField(
        required=False,
        label=_("Cause principale"),
        widget=forms.Textarea(attrs={'class': 'form-control form-control-solid', 'rows': 2})
    )
    
    consequence_pa = forms.CharField(
        required=False,
        label=_("Quelle en serait la conséquence ?"),
        widget=forms.Textarea(attrs={'class': 'form-control form-control-solid', 'rows': 2})
    )
    
    solution_pa = forms.CharField(
        required=False,
        label=_("Quelle est la solution à votre avis ?"),
        widget=forms.Textarea(attrs={'class': 'form-control form-control-solid', 'rows': 2})
    )

    location = forms.CharField(
        required=False,
        label=_("Lieu (saisie manuelle)"),
        widget=forms.TextInput(attrs={'class': 'form-control form-control-solid'}),
        help_text=_("Précisez l'emplacement exact si nécessaire")
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['site'].queryset = Site.objects.get_user_sites(user)

        # Sélection automatique si un seul site
        if self.fields['site'].queryset.count() == 1:
            self.initial['site'] = self.fields['site'].queryset.first()
            # Charge aussi les emplacements pour ce site
            self.fields['emplacement'].queryset = Emplacement.objects.filter(site=self.initial['site'])
            
            # Initialise le queryset des emplacements si un site est déjà sélectionné
            if 'site' in self.data:
                try:
                    site_id = int(self.data.get('site'))
                    self.fields['emplacement'].queryset = Emplacement.objects.filter(site_id=site_id)
                except (ValueError, TypeError):
                    pass
            elif self.instance.pk and self.instance.site:
                self.fields['emplacement'].queryset = self.instance.site.emplacements.all()
            else:
                self.fields['emplacement'].queryset = Emplacement.objects.none()
        
        # Configuration initiale des champs conditionnels
        if self.instance.pk:
            if self.instance.type_incident == 'PA':
                self.initial.update({
                    'blessure_potentielle': self.instance.blessure_potentielle,
                    'cause_principale': self.instance.cause_principale,
                    'consequence_pa': self.instance.consequence_pa,
                    'solution_pa': self.instance.solution_pa,
                })
            elif self.instance.type_incident == 'OSE':
                self.initial.update({
                    'consequence_ose': self.instance.consequence_ose,
                    'solution_ose': self.instance.solution_ose,
                    'action_correction': self.instance.action_correction,
                    'photo_correction': self.instance.photo_correction,
                    'commentaire_correction': self.instance.commentaire_correction,
                })
                
    class Meta:
        model = Incident
        fields = [
            'name', 'site', 'emplacement', 'location', 'type_incident',
             'photo', 'description', 'comment',
            'blessure_potentielle', 'cause_principale', 'consequence_pa', 'solution_pa',
            'consequence_ose', 'solution_ose', 'action_correction', 'photo_correction', 'commentaire_correction'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-control-solid'}),
            'site': forms.Select(attrs={'class': 'form-control form-control-solid'}),
            'emplacement': forms.Select(attrs={'class': 'form-control form-control-solid'}),
            'description': forms.Textarea(attrs={'class': 'form-control form-control-solid', 'rows': 2, 'cols': 40}),
            'comment': forms.Textarea(attrs={'class': 'form-control form-control-solid', 'rows': 2, 'cols': 40}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control form-control-solid'}),
        }
        labels = {
            'name': _('Intitulé de l\'évènement'),
            'site': _('Site'),
            'emplacement': _('Emplacement'),
            'photo': _('Photo de l\'évènement'),
            'description': _('Description détaillée'),
            'comment': _('Commentaire'),
        }

    def clean(self):
        cleaned_data = super().clean()
        type_incident = cleaned_data.get('type_incident')
        
        # Validation des champs PA
        if type_incident == 'Presque-Accident':
            if not cleaned_data.get('blessure_potentielle') in [True, False]:
                self.add_error('blessure_potentielle', 'Ce champ est obligatoire pour les PA')
            if not cleaned_data.get('cause_principale'):
                self.add_error('cause_principale', 'Ce champ est obligatoire pour les PA')
            if not cleaned_data.get('consequence_pa'):
                self.add_error('consequence_pa', 'Ce champ est obligatoire pour les PA')
            if not cleaned_data.get('solution_pa'):
                self.add_error('solution_pa', 'Ce champ est obligatoire pour les PA')
        
        # Validation des champs OSE
        elif type_incident == 'Observation Sécurité/Environnement':
            if not cleaned_data.get('consequence_ose'):
                self.add_error('consequence_ose', 'Ce champ est obligatoire pour les OSE')
            if not cleaned_data.get('solution_ose'):
                self.add_error('solution_ose', 'Ce champ est obligatoire pour les OSE')
            if cleaned_data.get('action_correction') and not cleaned_data.get('photo_correction'):
                self.add_error('photo_correction', 'Une photo est requise pour les corrections immédiates')

        return cleaned_data

class AssignUserForm(forms.ModelForm):
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.none(),
        label="Assigner à",
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'style': 'width: 100%; padding: 2px; border-radius: 5px;',
        }),
    )

    class Meta:
        model = Incident
        fields = ['assigned_to'] 
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrage des utilisateurs qui peuvent être assignés à des incidents
        self.fields['assigned_to'].queryset = User.objects.filter(
            is_active=True,
            groups__permissions__codename__in=['change_incident']  
        )
