from django.contrib.contenttypes.models import ContentType
from .models import Notification, User

class NotificationService:
    @staticmethod
    def send_notification(user, title, message, content_object=None):
        """
        Envoie une notification à un utilisateur.

        :param user: L'utilisateur destinataire de la notification.
        :param title: Le titre de la notification.
        :param message: Le message de la notification.
        :param content_object: L'objet associé à la notification (optionnel).
        :return: L'objet Notification créé.
        """
        content_type = None
        object_id = None

        if content_object:
            content_type = ContentType.objects.get_for_model(content_object)
            object_id = content_object.id

        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            content_type=content_type,
            object_id=object_id,
        )
        return notification