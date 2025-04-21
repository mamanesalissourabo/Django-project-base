from django.db import models
from django_fsm import FSMField, transition, RETURN_VALUE, GET_STATE
from simple_history.models import HistoricalRecords
from base.models import Emplacement, Site, User
from reward.models import UserProfile
from django.utils import timezone
from django.utils.text import slugify
import logging

logger = logging.getLogger(__name__)

class IncidentStatuses(models.TextChoices):
    """
    Définit les différents statuts possibles pour un incident.

    Ces choix représentent les étapes du cycle de vie d'un incident.
    """
    PENDING = 'pending', 'En attente'
    ONGOING = 'ongoing', 'En cours'
    RESOLVED = 'resolved', 'Résolu'
    DONE = 'done', 'Cloturé'

class Incident(models.Model):
    TYPE_CHOICES = [
        ('PA', 'PA'),
        ('OSE', 'OSE'),
    ]

    class Meta:
        default_permissions = ['add', 'change', 'view']
        permissions = [
            ("can_change_incident_status", "Peut changer le statut des incidents"),
            ("can_assign_user", "Peut assigner un incident a des utilisateurs"),
        ]
    reference = models.CharField(max_length=20, unique=True, editable=False, blank=True )
    name = models.CharField(max_length=255)
    report_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True, verbose_name="Description de l'évènement")
    location = models.CharField(max_length=50, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    status = FSMField(default=IncidentStatuses.PENDING, choices=IncidentStatuses.choices, verbose_name="État", protected=False)
    #criticity = models.CharField( max_length=50, choices=[('low', 'Faible'), ('medium', 'Moyenne'), ('high', 'Élevée')], blank=True, null=True)
    created_by_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT, related_name="created_incident")
    updated_by_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT, related_name="updated_incident")
    assigned_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT, related_name="assigned_user")
    site = models.ForeignKey(Site, on_delete=models.PROTECT, related_name='incidents', blank=True, null=True)
    emplacement = models.ForeignKey(Emplacement, on_delete=models.PROTECT, related_name='incidents', blank=True, null=True, verbose_name="Emplacement spécifique")
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)  
    type_incident = models.CharField(max_length=3, choices=TYPE_CHOICES, blank=True, null=True)
    # Champs spécifiques PA
    blessure_potentielle = models.BooleanField(null=True, blank=True)
    cause_principale = models.TextField(blank=True, null=True)
    consequence_pa = models.TextField(blank=True, null=True)
    solution_pa = models.TextField(blank=True, null=True)
    # Champs spécifiques OSE
    consequence_ose = models.TextField(blank=True, null=True)
    solution_ose = models.TextField(blank=True, null=True)
    action_correction = models.BooleanField(null=True, blank=True)
    photo_correction = models.ImageField(upload_to='photos/', null=True, blank=True)
    commentaire_correction = models.TextField(blank=True, null=True)
    history = HistoricalRecords(table_name="incident_history")
    
    # Méthode pour déterminer si c'est un PA ou OSE
    def is_pa(self):
        return self.type_incident == 'PA'
    
    def is_ose(self):
        return self.type_incident == 'OSE'
    
    # Transitions entre les statuts

    @transition(field=status, source=IncidentStatuses.PENDING, target=IncidentStatuses.ONGOING, permission='incident.can_change_incident_status')
    def start_work(self):
        """Démarre le traitement de l'incident."""
        self._status_changed = True

    @transition(field=status, source=IncidentStatuses.ONGOING, target=IncidentStatuses.RESOLVED)
    def close_work(self):
        """Marque l'incident comme résolu."""
        self._status_changed = True

    @transition(field=status, source=IncidentStatuses.RESOLVED, target=IncidentStatuses.DONE)
    def mark_as_done(self):
        """Marquer l'incident comme 'Cloturé'."""
        self._status_changed = True
  

    def __str__(self):
        return self.reference
    
    @classmethod
    def get_next_reference(cls):
        """Génère la prochaine référence séquentielle au format INC-000001"""
        last_incident = cls.objects.order_by('-id').first()
        if last_incident and last_incident.reference:
            try:
                last_num = int(last_incident.reference.split('-')[-1])
                return f"INC-{last_num + 1:06d}"  # Format à 6 chiffres
            except (ValueError, IndexError):
                pass
        return "INC-000001" 
    
    def save(self, *args, **kwargs):
        # Générer la référence seulement à la création
        if not self.pk and not self.reference:
            logger.info(f"Génération référence pour incident {self.id}")
            self.reference = self.get_next_reference()
        
        if hasattr(self, '_status_changed') and self._status_changed:
            self.updated_by_user = self.assigned_to or self.updated_by_user
        
        super().save(*args, **kwargs)
    