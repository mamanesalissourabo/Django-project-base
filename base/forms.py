from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _  # Import gettext_lazy for translation

from crispy_forms.helper import FormHelper
from dal import autocomplete

from base.models import User,Perimeter, Notification

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label=_("Nom d'utilisateur"),  # Texte de base en français
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-transparent',
            'placeholder': _("Nom d'utilisateur")
        })
    )
    password = forms.CharField(
        label=_("Mot de passe"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control bg-transparent', 
            'placeholder': _("Mot de passe")
        })
    )


class UserProfileForm(forms.ModelForm):
    """
    Formulaire de profil utilisateur.

    Ce formulaire permet de modifier les informations personnelles d'un utilisateur, 
    notamment son prénom, son nom, sa société, son numéro de téléphone, son email, 
    son adresse et sa photo de profil.
    
    """
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'adresse', 'company', 'photo')

    def __init__(self, *args, **kwargs):
        """
        Initialisation du formulaire avec des attributs CSS personnalisés 
        pour chaque champ.
        
        """
        super(UserProfileForm, self).__init__(*args, **kwargs)
        
        # Configuration des attributs pour chaque champ
        self.fields['first_name'].widget.attrs.update(
            {'class': "form-control form-control-lg form-control-solid mb-3 mb-lg-0",
             'placeholder': 'Prénom'})
        
        self.fields['last_name'].widget.attrs.update(
            {'class': "form-control form-control-lg form-control-solid",
             'placeholder': 'Nom de famille'})
        
        self.fields['email'].widget.attrs.update(
            {'class': "form-control form-control-lg form-control-solid",
             'placeholder': 'Adresse email'})
        
        self.fields['phone'].widget.attrs.update(
            {'class': "form-control form-control-lg form-control-solid",
             'placeholder': 'Numéro de téléphone'})
        
        self.fields['adresse'].widget.attrs.update(
            {'class': "form-control form-control-lg form-control-solid",
             'placeholder': 'Adresse'})
        
        self.fields['company'].widget.attrs.update(
            {'class': "form-control form-control-lg form-control-solid",
             'placeholder': 'Société'})
        
        self.fields['photo'].widget.attrs.update(
            {'class': "form-control form-control-lg form-control-solid"})
        # self.fields['notif_email'].widget.attrs.update({'class': "form-check-input w-45px h-30px"})


class PerimeterAdminForm(forms.ModelForm):
    """
    Formulaire d'administration pour le modèle Perimeter.

    Ce formulaire inclut un champ parent utilisant une sélection automatique
    grâce à Django Autocomplete Light (DAL), permettant une recherche simplifiée.
    
    """
    class Meta:
        model = Perimeter
        fields = ('__all__')
        widgets = {
            'parent': autocomplete.ModelSelect2(url='perimeter-autocomplete',
                forward=['site',],),
        }


class FilterFormHelper(FormHelper):
    """
    Helper pour les formulaires de filtres avec Crispy Forms.

    - Désactive l'inclusion automatique de la balise <form>.
    - Configure les classes CSS pour une mise en page flexible et compacte.
    - Masque les étiquettes des champs pour une présentation simplifiée.
   
    """
    form_tag = False
    form_class = 'd-flex flex-column flex-md-row gap-5'
    field_class = 'flex-row-fluid mae-filter-form input-group-sm'
    help_text_inline = True
    form_show_labels = False
    include_media = False

class NotificationFilterFormHelper(FilterFormHelper):
    """
    Helper pour les formulaires de filtres spécifiques au modèle Notification.

    Hérite de FilterFormHelper et configure l'affichage pour le modèle Notification.
    
    """
    model = Notification