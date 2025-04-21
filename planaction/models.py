from django.db import models

from django_fsm import FSMField, transition, RETURN_VALUE, GET_STATE
from incident.models import Incident
from base.models import User

from simple_history.models import HistoricalRecords

import logging
logger = logging.getLogger(__name__)

class PlanActionStatuses(models.TextChoices):
    """
    Définit les différents statuts possibles pour un incident.
    Ces choix représentent les étapes du cycle de vie d'un incident.
    """
    PENDING = 'pending', 'En attente'
    ONGOING = 'ongoing', 'En cours'
    RESOLVED = 'resolved', 'Résolu'
    DONE = 'done', 'Cloturé'

class PlanAction(models.Model):

    class Meta:
        default_permissions = ['add', 'change', 'view']

    reference = models.CharField(max_length=20, unique=True, editable=False, blank=True )
    title = models.CharField(max_length=255, verbose_name="Titre de l'action")
    incident = models.ForeignKey(Incident, null=True, blank=True, on_delete=models.PROTECT, related_name='plan_actions')
    created_by_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT, related_name="created_planaction")
    updated_by_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT, related_name="updated_planaction")
    description = models.TextField(verbose_name="Description")
    creation_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = FSMField(default=PlanActionStatuses.PENDING, choices=PlanActionStatuses.choices, verbose_name="État de l'action", protected=False)
    history = HistoricalRecords(table_name="planaction_history")  

    @transition(field=status, source=PlanActionStatuses.PENDING, target=PlanActionStatuses.ONGOING)
    def start_work(self):
        """Démarre le traitement de l'incident."""
        self._status_changed = True

    @transition(field=status, source=PlanActionStatuses.ONGOING, target=PlanActionStatuses.RESOLVED)
    def close_work(self):
        """Marque l'incident comme résolu."""
        self._status_changed = True

    @transition(field=status, source=PlanActionStatuses.RESOLVED, target=PlanActionStatuses.DONE)
    def mark_as_done(self):
        """Marquer l'incident comme 'Cloturé'."""
        self._status_changed = True
  

    def __str__(self):
        return self.title

    @classmethod
    def get_next_reference(cls):
        """Génère la prochaine référence séquentielle au format ACT-000001"""
        last_incident = cls.objects.order_by('-id').first()
        if last_incident and last_incident.reference:
            try:
                last_num = int(last_incident.reference.split('-')[-1])
                return f"ACT-{last_num + 1:06d}" 
            except (ValueError, IndexError):
                pass
        return "ACT-000001" 
    
    def save(self, *args, **kwargs):
        # Générer la référence seulement à la création
        if not self.pk and not self.reference:
            logger.info(f"Génération référence pour incident {self.id}")
            self.reference = self.get_next_reference()
        
        if hasattr(self, '_status_changed') and self._status_changed:
            self.updated_by_user = self.created_by_user or self.updated_by_user
        
        super().save(*args, **kwargs)
    
