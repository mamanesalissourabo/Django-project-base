# worksafety2/celery.py
import os
from celery import Celery
from django.conf import settings

# Définir le module de paramètres Django par défaut
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'worksafety2.settings')

# Initialiser l'application Celery
app = Celery('worksafety2')

# Charger les paramètres depuis Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Configuration supplémentaire
app.conf.update(
    task_serializer='json',
    timezone='America/New_York',
)

# Découverte automatique des tâches dans les applications Django
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)