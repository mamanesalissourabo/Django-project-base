from django.db import models

from base.models import User
from simple_history.models import HistoricalRecords

class FAQCategory(models.Model):
    """Defines categories for support tickets."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(verbose_name="Description", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords(table_name="faq_category_history")

    def __str__(self):
        return self.name

class FAQ(models.Model):
    """Defines a model for frequently asked questions."""
    question = models.CharField(max_length=255)
    answer = models.TextField()
    category = models.ForeignKey(
        FAQCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="faqs"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords(table_name="faq_question_history")

    def __str__(self):
        return self.question
    
class SupportTicket(models.Model):
    #user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=100, verbose_name="Prénom")
    last_name = models.CharField(max_length=100, verbose_name="Nom")
    email = models.EmailField(verbose_name="Email")
    title = models.CharField(max_length=200, verbose_name="Titre du message")
    message = models.TextField(verbose_name="Message")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    def __str__(self):
        return f"Ticket #{self.id} - {self.title}"

    class Meta:
        verbose_name = "Ticket de support"
        verbose_name_plural = "Tickets de support"
        ordering = ['-created_at']