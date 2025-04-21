from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from reward.models import UserProfile, Bonus
from base.models import User
from reward.tasks import calculate_weekly_bonus, calculate_monthly_bonus, calculate_quarterly_bonus

class BonusTasksTestCase(TestCase):
    def setUp(self):
        # Créer un utilisateur et un profil
        self.user = User.objects.create(username='testuser')
        self.profile = UserProfile.objects.create(user=self.user, total_points=0)

    def test_weekly_bonus(self):
        # Simuler une activité il y a 6 jours (éligible pour le bonus hebdomadaire)
        self.profile.last_activity_date = timezone.now() - timedelta(days=6)
        self.profile.save()

        # Exécuter la tâche hebdomadaire
        calculate_weekly_bonus()

        # Vérifier que le bonus a été attribué
        self.assertEqual(Bonus.objects.filter(user=self.user, bonus_type='weekly').count(), 1)
        self.assertEqual(UserProfile.objects.get(user=self.user).total_points, 6)

    def test_monthly_bonus(self):
        # Simuler une activité il y a 29 jours (éligible pour le bonus mensuel)
        self.profile.last_activity_date = timezone.now() - timedelta(days=29)
        self.profile.save()

        # Exécuter la tâche mensuelle
        calculate_monthly_bonus()

        # Vérifier que le bonus a été attribué
        self.assertEqual(Bonus.objects.filter(user=self.user, bonus_type='monthly').count(), 1)
        self.assertEqual(UserProfile.objects.get(user=self.user).total_points, 3)

    def test_quarterly_bonus(self):
        # Simuler une activité il y a 89 jours (éligible pour le bonus trimestriel)
        self.profile.last_activity_date = timezone.now() - timedelta(days=89)
        self.profile.save()

        # Exécuter la tâche trimestrielle
        calculate_quarterly_bonus()

        # Vérifier que le bonus a été attribué
        self.assertEqual(Bonus.objects.filter(user=self.user, bonus_type='quarterly').count(), 1)
        self.assertEqual(UserProfile.objects.get(user=self.user).total_points, 1)