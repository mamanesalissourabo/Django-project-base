import os
from django.conf import settings
from celery import Celery

# Initialisation de l'application Celery
app = Celery('worksafety2')

# Chargement des paramètres depuis Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Configuration supplémentaire
app.conf.update(
    task_serializer='json',
    timezone='America/New_York',
)