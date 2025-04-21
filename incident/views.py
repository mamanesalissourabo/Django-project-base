# views.py
from itertools import count
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.core.exceptions import PermissionDenied

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, View
from django.contrib import messages
from django.http import JsonResponse

from base.models import Emplacement, Site

from .models import Incident, IncidentStatuses
from .forms import IncidentForm
from django.db.models import Count, Q  
from datetime import datetime, timedelta
from django.utils import timezone
from reward.models import UserProfile
from .forms import AssignUserForm  
from .filters import IncidentListFilter
from django_filters.views import FilterView
from .filters import IncidentListFilter 
from django.core.paginator import Paginator
from .exports import export_incidents_to_excel
from django.views.generic import CreateView
from django.urls import reverse_lazy

# def incident_delete(request, pk):
#     incident = get_object_or_404(Incident, pk=pk)
#     if request.method == "POST":
#         incident.delete()
#         return redirect('incident_list')
#     return render(request, 'incident/incident_confirm_delete.html', {'incident': incident})


class IncidentCreateView(CreateView):
    model = Incident
    form_class = IncidentForm
    template_name = 'incident/incident_create.html'
    success_url = reverse_lazy('incident_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        print("Emplacement value:", form.cleaned_data.get('emplacement'))
        form.instance.created_by_user = self.request.user
        form.instance.updated_by_user = self.request.user
        
        emplacement_id = self.request.POST.get('emplacement')
        if emplacement_id:
            try:
                form.instance.emplacement = Emplacement.objects.get(id=emplacement_id)
            except Emplacement.DoesNotExist:
                pass
            
        # Auto-assignation si un seul site disponible
        if not form.instance.site:
            user_sites = Site.objects.get_user_sites(self.request.user)
            if user_sites.count() == 1:
                form.instance.site = user_sites.first()
                
        return super().form_valid(form)

@login_required
@permission_required('incident.view_incident', raise_exception=True)
def incident_detail(request, pk):
    incident = get_object_or_404(Incident, pk=pk)
    
    # Gérer l'assignation d'un utilisateur
    if request.method == "POST" and 'assign_user' in request.POST:
        # Vérifier si l'incident peut encore être assigné
        if incident.status in ['ongoing', 'resolved', 'done']:
            messages.warning(request, "Cet incident ne peut plus être assigné car son statut est déjà en cours ou terminé.")
            return redirect('incident_detail', pk=incident.pk)
        
        # Si l'incident peut être assigné, traiter le formulaire
        form = AssignUserForm(request.POST, instance=incident)
        if form.is_valid():
            form.save()
            messages.success(request, "L'utilisateur a été assigné avec succès.")
            return redirect('incident_detail', pk=incident.pk)
    else:
        form = AssignUserForm(instance=incident)
    
    # Gérer le changement de statut
    if request.method == "POST" and 'change_status' in request.POST:
        if incident.assigned_to != request.user:
            messages.warning(request, "Vous n'êtes pas assigné à cet incident et ne pouvez pas modifier son statut.")
            return redirect('incident_detail', pk=incident.pk)
        
        if incident.status == "done":
            messages.warning(request, "Cet incident est déjà marqué comme 'Cloturé' et ne peut plus être modifié.")
            return redirect('incident_detail', pk=incident.pk)
        
        # Déterminer la prochaine action en fonction du statut actuel
        if incident.status == "pending":
            incident.start_work()
        elif incident.status == "ongoing":
            incident.close_work()
        elif incident.status == "resolved":
            incident.mark_as_done()
        
        incident.save()
        messages.success(request, f"Le statut de l'incident a été mis à jour : {incident.status}")
        return redirect('incident_detail', pk=incident.pk)
    
    context = {
        'incident': incident,
        'form': form,
        'can_change_status': request.user.has_perm('incident.can_change_incident_status'),
        'can_assign_user': request.user.has_perm('incident.can_assign_user'),
    }
    return render(request, 'incident/incident_detail.html', context)

@login_required
def incident_update(request, pk):
    incident = get_object_or_404(Incident, pk=pk)
    if request.method == "POST":
        form = IncidentForm(request.POST, request.FILES, instance=incident)
        if form.is_valid():
            incident = form.save(commit=False)
            incident.updated_by_user = request.user
            incident.save()
            # Redirection conditionnelle
            next_url = request.GET.get('next', 'incident_detail')
            return redirect(next_url, pk=incident.pk)
    else:
        form = IncidentForm(instance=incident)
    return render(request, 'incident/incident_update.html', {'form': form})


@login_required
@permission_required('incident.view_incident', raise_exception=True)
def incident_list(request):
    if not request.user.has_perm('incident.view_incident'):
        return HttpResponseForbidden("Vous n'avez pas la permission de voir les incidents.")
    
    # Récupération de base des incidents
    if request.user.is_superuser:
        incidents = Incident.objects.all()
    else:
        incidents = Incident.objects.filter(created_by_user=request.user)
    
    # Ajout des incidents assignés si permission
    if request.user.has_perm('incident.can_view_assigned_incidents'):
        assigned_incidents = Incident.objects.filter(assigned_to=request.user)
        incidents = incidents | assigned_incidents
    
    # Gestion du tri 
    sort_field = request.GET.get('sort')
    default_sort = '-report_date'
    
    allowed_fields = {
        'reference': 'reference',
        '-reference': '-reference',
        'name': 'name',
        '-name': '-name',
        'report_date': 'report_date',
        '-report_date': '-report_date',
        'site': 'site',
        '-site': '-site',
        'description': 'description',
        '-description': '-description',
        'status': 'status',
        '-status': '-status',
        'type_incident': 'type_incident',
        '-type_incident': '-type_incident',
        'emplacement':'emplacement',
        '-emplacement':'-emplacement',
    }
    
    # Validation et application du tri
    sort_field = allowed_fields.get(sort_field, default_sort)
    incidents = incidents.order_by(sort_field)
    
    # Application des filtres 
    incident_filter = IncidentListFilter(request.GET, queryset=incidents.distinct())

    if 'export' in request.GET:
        return export_incidents_to_excel(incident_filter.qs)
    
    # Pagination
    per_page = request.GET.get('per_page', 5)
    paginator = Paginator(incident_filter.qs, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Gestion du formulaire
    if request.method == "POST":
        form = IncidentForm(request.POST, request.FILES)
        if form.is_valid():
            incident = form.save(commit=False)
            incident.created_by_user = request.user
            incident.save()
            messages.success(request, "L'incident a été créé avec succès.")
            return redirect('incident_list')
    else:
        form = IncidentForm()
    
    # Contexte avec le champ de tri actif
    context = {
        'form': form,
        'filter': incident_filter,
        'incidents': page_obj,
        'sort_field': sort_field,  # Important pour les icônes
        'is_superuser': request.user.is_superuser,
        'can_change_status': request.user.has_perm('incident.can_change_incident_status'),
    }
    return render(request, 'incident/incident_list.html', context)


def get_emplacements(request):
    site_id = request.GET.get('site_id')
    emplacements = Emplacement.objects.filter(site_id=site_id).values('id', 'name')
    return JsonResponse(list(emplacements), safe=False)