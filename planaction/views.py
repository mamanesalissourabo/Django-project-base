from django.shortcuts import render

from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from planaction.filters import PlanActionListFilter
from planaction.models import PlanAction
from planaction.forms import PlanActionForm
from django.shortcuts import get_object_or_404

from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.contrib import messages
from django.views.generic import CreateView
from django.db.models import Count, Q  
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.paginator import Paginator


class PlanActionCreateView(CreateView):
    model = PlanAction
    form_class = PlanActionForm
    template_name = 'planaction/planaction_create.html'
    success_url = reverse_lazy('planaction-list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user 
        return kwargs
    
    def form_valid(self, form):
        # Définit automatiquement l'utilisateur connecté
        form.instance.created_by_user = self.request.user
        form.instance.updated_by_user = self.request.user
        return super().form_valid(form)

class PlanActionListAndCreateView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'planaction/planaction_list.html'
    permission_required = 'planaction.view_planaction'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Récupération de base des plans d'action
        if self.request.user.is_superuser:
            plan_actions = PlanAction.objects.all()
        else:
            plan_actions = PlanAction.objects.filter(
                Q(created_by_user=self.request.user) | 
                Q(responsible_users=self.request.user)
            ).distinct()
        
        # Gestion du tri
        sort_field = self.request.GET.get('sort', '-creation_date')
        allowed_fields = {
            'reference': 'reference',
            '-reference': '-reference',
            'title': 'title',
            '-title': '-title',
            'creation_date': 'creation_date',
            '-creation_date': '-creation_date',
            'status': 'status',
            '-status': '-status',
            'created_by_user': 'created_by_user',
            '-created_by_user': '-created_by_user',
        }
        
        sort_field = allowed_fields.get(sort_field, '-creation_date')
        plan_actions = plan_actions.order_by(sort_field)
        
        # Application des filtres
        plan_action_filter = PlanActionListFilter(self.request.GET, queryset=plan_actions)
        
        # Pagination
        per_page = self.request.GET.get('per_page', 5)
        paginator = Paginator(plan_action_filter.qs, per_page)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context.update({
            'form': PlanActionForm(),
            'filter': plan_action_filter,
            'planactions': page_obj,
            'sort_field': sort_field,
            'is_superuser': self.request.user.is_superuser,
        })
        return context
    
    def post(self, request, *args, **kwargs):
        form = PlanActionForm(request.POST)
        if form.is_valid():
            plan_action = form.save(commit=False)
            plan_action.created_by_user = request.user
            plan_action.save()
            form.save_m2m()  # Pour les many-to-many fields
            messages.success(request, 'Plan d\'action créé avec succès.')
            return redirect('planaction-list')
        
        # Si le formulaire n'est pas valide, réafficher la page avec les erreurs
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)

    
class PlanActionDetailView(DetailView, UpdateView):
    model = PlanAction
    form_class = PlanActionForm
    template_name = 'planaction/planaction_detail.html'
    context_object_name = 'planaction'
    success_url = reverse_lazy('planaction_list')

    def get_object(self, queryset=None):
        # Récupère l'objet PlanAction à afficher ou à modifier
        return get_object_or_404(PlanAction, pk=self.kwargs.get('pk'))

    def get_context_data(self, **kwargs):
        # Ajoute le formulaire au contexte pour la modale de modification
        context = super().get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = self.get_form()
        return context
    
        context['can_change_status'] = self.request.user.has_perm('planaction.change_planaction')
        return context

    def post(self, request, *args, **kwargs):
        
        self.object = self.get_object()
        
        # Gestion du changement de statut
        if 'change_status' in request.POST:
            if not request.user.has_perm('planaction.change_planaction'):
                messages.warning(request, "Vous n'avez pas la permission de modifier le statut.")
                return redirect('planaction-detail', pk=self.object.pk)
            
            if self.object.status == "done":
                messages.warning(request, "Cette action est déjà marquée comme 'Cloturée'")
                return redirect('planaction-detail', pk=self.object.pk)
            
            # Transition des statuts
            if self.object.status == "pending":
                self.object.start_work()
            elif self.object.status == "ongoing":
                self.object.close_work()
            elif self.object.status == "resolved":
                self.object.mark_as_done()
            
            self.object.save()
            messages.success(request, f"Statut mis à jour : {self.object.get_status_display()}")
            return redirect('planaction-detail', pk=self.object.pk)

        # Gère la soumission du formulaire de modification
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        # Enregistre les modifications et redirige vers la page de détails
        form.save()
        return super().form_valid(form)
    
class PlanActionDeleteView(DeleteView):
    model = PlanAction
    template_name = 'planaction/planaction_confirm_delete.html'
    success_url = reverse_lazy('planaction-list')

