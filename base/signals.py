from django.db.models.signals import post_save
from django.dispatch import receiver
from reward.models import UserProfile  # Utiliser UserProfile au lieu de UserPoints
from .services import NotificationService

@receiver(post_save, sender=UserProfile)
def send_points_notification(sender, instance, **kwargs):
    """
    Envoie une notification à l'utilisateur lorsque son total de points est mis à jour.
    """
    user = instance.user
    total_points = instance.total_points

    # Envoyer la notification
    NotificationService.send_notification(
        user,
        title="Votre total de points",
        message=f"Vous avez maintenant {total_points} points."
    )