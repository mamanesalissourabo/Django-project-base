from django import forms
from .models import SupportTicket

class SupportTicketForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ['first_name', 'last_name', 'email', 'title', 'message']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control form-control-solid'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control form-control-solid'}),
            'email': forms.EmailInput(attrs={'class': 'form-control form-control-solid'}),
            'title': forms.TextInput(attrs={
                'class': 'form-control form-control-solid',
                'placeholder': 'Sujet de votre demande'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control form-control-solid',
                'rows': 2,
                'placeholder': 'Décrivez votre problème ou demande...'
            }),
        }