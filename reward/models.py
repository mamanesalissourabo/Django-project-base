from django.db import models
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField('base.User', on_delete=models.CASCADE, related_name='reward_profile')
    total_points = models.IntegerField(default=0)  # Score total de l'utilisateur
    last_incident_date  = models.DateTimeField(null=True, blank=True)  # Date de la dernière activité (incident signalé)
    allowed_sites = models.ManyToManyField('base.Site', blank=True, null=True, related_name='authorized_users')
    
    def add_allowed_site(self, site):
        """Ajoute un site à la liste des sites autorisés"""
        self.allowed_sites.add(site)
        self.save()
    
    def get_accessible_sites(self):
        return self.allowed_sites.all()

    def __str__(self):
        return f"Profil de {self.user.first_name}"
    
    def get_incident_count(self):
        """Retourne le nombre d'incidents déclarés par l'utilisateur."""
        return self.user.created_incident.count()  

    def get_total_bonus(self):
        """Retourne le total des bonus attribués à l'utilisateur."""
        return self.user.bonuses.aggregate(total_bonus=models.Sum('points'))['total_bonus'] or 0

class Bonus(models.Model):
    user = models.ForeignKey('base.User', on_delete=models.CASCADE, related_name='bonuses')
    bonus_type = models.CharField(max_length=20, choices=[
        ('weekly', 'Hebdomadaire'),
        ('monthly', 'Mensuel'),
        ('quarterly', 'Trimestriel'),
    ], verbose_name='frequence')
    points = models.IntegerField()  # Points attribués
    date_awarded = models.DateTimeField(auto_now_add=True, verbose_name='Date d\'attribution')  # Date d'attribution du bonus

    def __str__(self):
        return f"{self.bonus_type} bonus for {self.user.first_name}"
