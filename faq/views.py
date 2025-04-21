from django.shortcuts import render, redirect
from .models import FAQCategory, FAQ
from django.contrib import messages
from .forms import SupportTicketForm

def faq_list(request):
    # Récupérer toutes les catégories et questions
    categories = FAQCategory.objects.all()
    faqs = FAQ.objects.select_related('category').all()
    
    # Passer les données au template
    return render(request, 'faq/faq_list.html', {
        'categories': categories,
        'faqs': faqs,
    })

def accueil(request):
    support_form = SupportTicketForm()  # Créez une instance du formulaire
    return render(request, 'faq/accueil.html', {
        'form': support_form  
    })


# def contact_support(request):
#     if request.method == 'POST':
#         form = SupportTicketForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Votre ticket a été envoyé avec succès!')
#             return redirect('contact_support')
#     else:
#         form = SupportTicketForm()

#     return render(request, 'support/contact.html', {'form': form})
from django.http import JsonResponse
from django.urls import reverse_lazy

def contact_support(request):
    if request.method == 'POST':
        form = SupportTicketForm(request.POST)
        if form.is_valid():
            form.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Requête AJAX
                return JsonResponse({
                    'success': True,
                    'redirect_url': reverse_lazy('accueil')  # Redirection vers l'accueil
                })
            else:
                # Requête normale
                messages.success(request, 'Votre ticket a été envoyé avec succès!')
                return redirect('accueil')  # Redirection vers l'accueil
    else:
        form = SupportTicketForm()

    return render(request, 'support/contact.html', {'form': form})