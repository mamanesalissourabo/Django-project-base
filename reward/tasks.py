from celery import shared_task
from django.conf import settings

from django.utils import timezone
from datetime import timedelta
from reward.models import UserProfile, Bonus

@shared_task
def calculate_weekly_bonus():
    """
    Cette tâche attribue un bonus de 6 points aux utilisateurs qui ont signalé au moins un incident dans la semaine écoulée.
    """
    # Récupérer tous les utilisateurs ayant signalé un incident cette semaine
    start_date = timezone.now() - timedelta(days=7)
    profiles = UserProfile.objects.filter(last_incident_date__gte=start_date)

    # Attribuer un bonus hebdomadaire
    for profile in profiles:
        Bonus.objects.create(user=profile.user, bonus_type='weekly', points=6)
        profile.total_points += 6
        profile.save()

@shared_task
def calculate_monthly_bonus():
    """
    Cette tâche attribue un bonus de 3 points aux utilisateurs qui ont signalé au moins un incident dans le mois écoulé.
    """
    # Récupérer tous les utilisateurs ayant signalé un incident ce mois-ci
    start_date = timezone.now() - timedelta(days=30)
    profiles = UserProfile.objects.filter(last_incident_date__gte=start_date)

    # Attribuer un bonus mensuel
    for profile in profiles:
        Bonus.objects.create(user=profile.user, bonus_type='monthly', points=3)
        profile.total_points += 3
        profile.save()

@shared_task
def calculate_quarterly_bonus():
    """
    Cette tâche attribue un bonus de 1 point aux utilisateurs qui ont signalé au moins un incident dans le trimestre écoulé.
    """
    # Récupérer tous les utilisateurs ayant signalé un incident ce trimestre
    start_date = timezone.now() - timedelta(days=90)
    profiles = UserProfile.objects.filter(last_incident_date__gte=start_date)

    # Attribuer un bonus trimestriel
    for profile in profiles:
        Bonus.objects.create(user=profile.user, bonus_type='quarterly', points=1)
        profile.total_points += 1
        profile.save()