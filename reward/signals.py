from django.db.models.signals import post_save
from django.dispatch import receiver
from incident.models import Incident
from reward.models import UserProfile
from base.models import User  
from django.utils import timezone


@receiver(post_save, sender=Incident)
def update_user_points(sender, instance, created, **kwargs):
    if created and instance.created_by_user:
        profile, created = UserProfile.objects.get_or_create(user=instance.created_by_user)
        profile.total_points += 2  # Ajouter 2 points pour chaque incident
        profile.last_incident_date = timezone.now()  # Mettre à jour la date de la dernière activité
        profile.save()