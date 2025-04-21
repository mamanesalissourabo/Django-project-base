from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from django.utils.decorators import method_decorator
from .models import Perimeter, User, Notification
from dal import autocomplete 
from django.db.models import Q

from django.urls import reverse_lazy
from django.views.generic import FormView
from . import forms
from base.forms import UserProfileForm
from .services import NotificationService
from django.utils import timezone
from worksafety2.context_processors import base_context


def logout_user(request):
    logout(request)
    return redirect('login')

class LoginView(FormView):
    """
    Vue de connexion pour les utilisateurs.

    Cette vue permet aux utilisateurs de se connecter via un formulaire d'authentification.
    Si l'utilisateur est déjà authentifié, il sera redirigé ailleurs en fonction de la configuration.
    """
    form_class = forms.CustomLoginForm  
    template_name = "authentification/login.html"  
    redirect_authenticated_user = False  
    success_url = reverse_lazy('accueil')  

    def get(self, request, *args, **kwargs):
        """
        Gère les requêtes GET. Redirige les utilisateurs déjà authentifiés si nécessaire.
        """
        if self.redirect_authenticated_user and request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Gère les soumissions de formulaire valides.
        """
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(self.request, username=username, password=password)

        if user is not None:
            login(self.request, user)
            return super().form_valid(form)
        else:
            form.add_error(None, "Identifiants invalides.")  # Ajouter une erreur non liée à un champ
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        """
        Ajoute des données supplémentaires au contexte du template.
        """
        context = super().get_context_data(**kwargs)
        context['message'] = self.request.session.pop('login_message', '')  # Récupérer un message de session
        return context

@login_required
def edit_profile(request):
    user = request.user

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # Redirigez l'utilisateur vers la page de profil après la modification
    else:
        form = UserProfileForm(instance=user)

    return render(request, 'base/edit_profile.html', {'form': form})


class PerimeterAutocomplete(autocomplete.Select2QuerySetView):
    """
    Vue de recherche pour l'autocomplétion des périmètres.
        
    Cette vue permet de filtrer les périmètres en fonction des critères de recherche fournis,
    tout en tenant compte de l'utilisateur authentifié et de ses permissions.

    Methods:
        get_queryset: Retourne la liste des périmètres correspondant aux critères de recherche.
        get_result_label: Retourne le libellé de chaque résultat.
        get_selected_result_label: Retourne le libellé du résultat sélectionné.
    """
    def get_queryset(self):
        site = self.forwarded.get('site', None)
        
        if not self.request.user.is_authenticated :
            return Perimeter.objects.none()
        
        qs = Perimeter.objects.with_tree_fields()
        
        if site and type(site) in (int, str) and site.isdigit():
            qs = qs.filter(Q(site__pk__in = [site]) | Q(site__isnull = True))
        elif site and type(site) == list:
            qs = qs.filter(Q(site__pk__in = site) | Q(site__isnull = True))

        if self.q:
            qs = qs.filter(Q(nom__icontains=self.q) | Q(external_id__icontains=self.q))

        return qs
    
    def get_result_label(self, result):
        return result.tree_label
    def get_selected_result_label(self, result):
        return str(result)
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PerimeterAutocomplete, self).dispatch(*args, **kwargs)

def send_points_notification(user, total_points):
    title = "Votre total de points"
    message = f"Vous avez actuellement {total_points} points."
    NotificationService.send_notification(user, title, message)

def announce_new_feature(users, feature_name):
    title = "Nouvelle fonctionnalité disponible"
    message = f"Une nouvelle fonctionnalité est disponible : {feature_name}."
    for user in users:
        NotificationService.send_notification(user, title, message)

@login_required
def list_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'base/notification_list.html', {'notifications': notifications})

@login_required
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    if not notification.read_at:
        notification.read_at = timezone.now()
        notification.save()
    return redirect('list_notifications')