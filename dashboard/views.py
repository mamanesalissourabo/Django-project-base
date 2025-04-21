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

from incident.models import Incident, IncidentStatuses
from incident.forms import IncidentForm
from django.db.models import Count, Q  
from datetime import datetime, timedelta
from django.utils import timezone
from reward.models import UserProfile
from worksafety2.context_processors import base_context


# @login_required
# @permission_required('incident.add_incident', raise_exception=True)
# @permission_required('incident.view_incident', raise_exception=True)
# @permission_required('incident.can_change_incident_status', raise_exception=True)
# def dashboard(request):
    
#     # Récupérer tous les incidents si l'utilisateur est un super utilisateur
#     if request.user.is_superuser:
#         incidents = Incident.objects.all()
#     else:
#         incidents = Incident.objects.filter(created_by_user=request.user)

#     # Calculer le nombre total d'incidents
#     total_incidents = incidents.count()
    
#     # Calculer la répartition des incidents par statut
#     status_count = {
#         'pending': incidents.filter(status='pending').count(),
#         'ongoing': incidents.filter(status='ongoing').count(),
#         'resolved': incidents.filter(status='resolved').count(),
#         'assigned': incidents.filter(assigned_to__isnull=False).count(),  # Incidents assignés
#     }

#     # Données pour le graphique en courbe (évolution par date)
#     # Récupérer les 30 derniers jours
#     end_date = timezone.now()
#     start_date = end_date - timedelta(days=30)

#     # Récupérer les incidents par date
#     incidents_by_date = (
#         incidents.filter(report_date__range=[start_date, end_date])
#         .extra({'report_date': "date(report_date)"})
#         .values('report_date')
#         .annotate(
#             total=Count('id'),
#             resolved=Count('id', filter=Q(status='resolved')),
#             ongoing=Count('id', filter=Q(status='ongoing')),
#             declared=Count('id', filter=Q(status='pending')),
#         )
#         .order_by('report_date')
#     )

#     # Formater les données pour Chart.js
#     dates = [entry['report_date'] for entry in incidents_by_date]
#     total_data = [entry['total'] for entry in incidents_by_date]
#     resolved_data = [entry['resolved'] for entry in incidents_by_date]
#     ongoing_data = [entry['ongoing'] for entry in incidents_by_date]
#     declared_data = [entry['declared'] for entry in incidents_by_date]

#     # Formater les dates en chaînes de caractères (YYYY-MM-DD)
#     dates = [entry['report_date'].strftime('%Y-%m-%d') for entry in incidents_by_date]

#    # Gérer le cas où UserProfile n'existe pas
#     try:
#         user_profile = UserProfile.objects.get(user=request.user)
#     except UserProfile.DoesNotExist:
#         # Créer un UserProfile par défaut sans le sauvegarder en base de données
#         user_profile = UserProfile(user=request.user, total_points=0, last_incident_date=None)

#     # Ajouter le contexte du classement si l'utilisateur est un superuser ou un admin
#     # if request.user.is_superuser or request.user.is_staff:
#     top_users = UserProfile.objects.order_by('-total_points')[:10]
#     ranked_users = []
#     for rank, profile in enumerate(top_users, start=1):
#         ranked_users.append({
#             'rank': rank,
#             'first_name': profile.user.first_name or "Utilisateur",
#             'last_name': profile.user.last_name or "",
#             'incident_count': profile.get_incident_count(),
#             'total_bonus': profile.get_total_bonus(),
#             'total_points': profile.total_points,
#         })
#     # else:
#     #     ranked_users = None

#     # Passer à la fois les incidents, le formulaire et les données du graphique au template
#     dashboard_context  = {
#         'incidents': incidents,
#         'total_incidents': total_incidents,
#         'user_profile': user_profile,
#         'status_count': status_count,
#         'is_superuser': request.user.is_superuser,
#         'dates': dates,
#         'total_data': total_data,
#         'resolved_data': resolved_data,
#         'ongoing_data': ongoing_data,
#         'declared_data': declared_data,
#         'ranked_users': ranked_users,
#     }

#     # Ajouter les données du helpdesk dashboard si l'utilisateur a la permission
#     if request.user.has_perm('incident.can_change_incident_status'):
#         helpdesk_incidents = Incident.objects.filter(assigned_to=request.user)
#         helpdesk_status_count = {
#             'pending': helpdesk_incidents.filter(status='pending').count(),
#             'ongoing': helpdesk_incidents.filter(status='ongoing').count(),
#             'resolved': helpdesk_incidents.filter(status='resolved').count(),
#             'done': helpdesk_incidents.filter(status='done').count(),
#         }

#         incidents_by_criticity = (
#             helpdesk_incidents
#             .values('criticity')  # Grouper par criticité
#             .annotate(total=Count('id'))  # Compter le nombre d'incidents par criticité
#             .order_by('criticity')  # Trier par criticité (low, medium, high)
#         )

#         criticity_labels = {
#             'low': 'Faible',
#             'medium': 'Moyenne',
#             'high': 'Élevée',
#         }

#         criticities = [criticity_labels[item['criticity']] for item in incidents_by_criticity]
#         totals = [item['total'] for item in incidents_by_criticity]

#         dashboard_context.update({
#             'helpdesk_total_incidents': helpdesk_incidents.count(),
#             'helpdesk_status_count': helpdesk_status_count,
#             'criticities': criticities,
#             'totals': totals,
#         })

#     context = base_context(request)  # Récupérer le contexte de base
#     context.update(dashboard_context)
    
#     return render(request, 'dashboard/dashboard.html', context)


@login_required
def dashboard(request):
    context = base_context(request)
    
    if request.user.is_superuser:
        incidents = Incident.objects.all()
        dashboard_type = 'superuser'
    elif request.user.has_perm('incident.can_change_incident_status'):
        incidents = Incident.objects.filter(assigned_to=request.user)
        dashboard_type = 'helpdesk'
    else:
        incidents = Incident.objects.filter(created_by_user=request.user)
        dashboard_type = 'normal'

    # Données communes
    common_data = {
        'total_incidents': incidents.count(),
        'status_count': {
            'pending': incidents.filter(status='pending').count(),
            'ongoing': incidents.filter(status='ongoing').count(),
            'resolved': incidents.filter(status='resolved').count(),
        },
        'dashboard_type': dashboard_type,
        'is_superuser': request.user.is_superuser,
    }

    # Données spécifiques superuser
    if dashboard_type == 'superuser':
        common_data['status_count']['assigned'] = incidents.filter(assigned_to__isnull=False).count()
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        incidents_by_date = (
            incidents.filter(report_date__range=[start_date, end_date])
            .extra({'report_date': "date(report_date)"})
            .values('report_date')
            .annotate(
                total=Count('id'),
                resolved=Count('id', filter=Q(status='resolved')),
                ongoing=Count('id', filter=Q(status='ongoing')),
                declared=Count('id', filter=Q(status='pending')),
            )
            .order_by('report_date')
        )
        common_data.update({
            'dates': [entry['report_date'].strftime('%Y-%m-%d') for entry in incidents_by_date],
            'total_data': [entry['total'] for entry in incidents_by_date],
            'resolved_data': [entry['resolved'] for entry in incidents_by_date],
            'ongoing_data': [entry['ongoing'] for entry in incidents_by_date],
            'declared_data': [entry['declared'] for entry in incidents_by_date],
        })

    # Données spécifiques helpdesk
    elif dashboard_type == 'helpdesk':
        incidents_by_criticity = (
            incidents.values('criticity')
            .annotate(total=Count('id'))
            .order_by('criticity')
        )
        criticity_labels = {'low': 'Faible', 'medium': 'Moyenne', 'high': 'Élevée'}
        common_data.update({
            'criticities': [criticity_labels[item['criticity']] for item in incidents_by_criticity],
            'totals': [item['total'] for item in incidents_by_criticity],
        })

    # Classement pour superuser et normal (mais masqué par défaut pour normal)
    if dashboard_type in ['superuser', 'normal']:
        top_users = UserProfile.objects.order_by('-total_points')[:10]
        common_data['ranked_users'] = [{
            'rank': rank,
            'first_name': profile.user.first_name or "Utilisateur",
            'last_name': profile.user.last_name or "",
            'incident_count': profile.get_incident_count(),
            'total_bonus': profile.get_total_bonus(),
            'total_points': profile.total_points,
        } for rank, profile in enumerate(top_users, start=1)]

    # UserProfile pour le score utilisateur
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile(user=request.user, total_points=0, last_incident_date=None)
    
    common_data['user_profile'] = user_profile
    context.update(common_data)
    return render(request, 'dashboard/dashboard.html', context)
