from django.db import models
from django.contrib.auth.models import UserManager
from django.db.models import query
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.contrib.auth import get_permission_codename
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from django.db.models import JSONField
from django_json_widget.widgets import JSONEditorWidget
from reward.models import UserProfile


class SoftDeleteQuerySet(query.QuerySet):
    """
    QuerySet personnalisé pour gérer la suppression douce.

    Cette classe surcharge la méthode `delete` pour éviter de supprimer réellement les objets,
    les marquant simplement comme supprimés avec un champ `deleted`.
    """
    def delete(self, using='default', *args, **kwargs):
        return

@admin.action(description="Supprimer les éléments sélectionnés", permissions=["soft_delete"])
def soft_delete(modeladmin, request, queryset):
    """
    Action personnalisée pour effectuer une suppression douce sur les objets sélectionnés.

    Cette action marque les objets comme supprimés au lieu de les supprimer physiquement.

    Args:
        modeladmin: L'instance de l'administrateur de modèle.
        request: La requête HTTP envoyée par l'utilisateur.
        queryset: Les objets sélectionnés à traiter.
    """
    for obj in queryset:
        with transaction.atomic():
            try:
                obj.soft_delete()
            except ValidationError as e:
                message = "Impossible de supprimer l'élément '{0}' : {1}".format(obj, e.message)
                modeladmin.message_user(request, message, level=messages.WARNING)
                return
    

class BaseModelManager(models.Manager):
    """
    Manager personnalisé pour les modèles avec suppression douce.

    Ce manager filtre les objets pour exclure ceux marqués comme supprimés (`deleted=True`),
    et fournit des méthodes supplémentaires pour gérer les objets supprimés.
    
    """

    def _get_base_queryset(self):
        """
        Retourne le queryset de base du modèle sans filtre de suppression douce.

        Returns:
            QuerySet: QuerySet de base du modèle.
        
        """
        return super(BaseModelManager, self).get_queryset()
        
    def _get_self_queryset(self):
        """
        Retourne un queryset filtré qui utilise SoftDeleteQuerySet.

        Returns:
            QuerySet: QuerySet filtré avec gestion de la suppression douce.
        
        """
        qs = self.get_queryset()
        if not issubclass(qs.__class__, SoftDeleteQuerySet):
            qs.__class__ = SoftDeleteQuerySet
        return qs
        
    def get_queryset(self):
        """
        Retourne un queryset filtré pour exclure les objets supprimés (deleted=False).

        Returns:
            QuerySet: QuerySet filtré pour exclure les objets supprimés.
        
        """
        qs = super(BaseModelManager, self).get_queryset().filter(deleted=False)
        if not issubclass(qs.__class__, SoftDeleteQuerySet):
            qs.__class__ = SoftDeleteQuerySet
        return qs

    def get(self, *args, **kwargs):
        """
        Récupère un objet selon les arguments fournis, avec gestion de la suppression douce.

        Args:
            *args: Arguments à passer à la méthode `get`.
            **kwargs: Paramètres de filtrage, y compris un identifiant (`pk`).

        Returns:
            Instance du modèle correspondante.
        
        """
        # if 'pk' in kwargs:
        #     return self.all_with_deleted().get(*args, **kwargs)
        # else:
        return self._get_self_queryset().get(*args, **kwargs)

    def filter(self, *args, **kwargs):
        """
        Filtre les objets en fonction des critères donnés, avec gestion de la suppression douce.

        Args:
            *args: Arguments de filtrage.
            **kwargs: Critères de filtrage.

        Returns:
            QuerySet: QuerySet filtré.
        
        """
        # if 'pk' in kwargs:
        #     qs = self.all_with_deleted().filter(*args, **kwargs)
        # else:
        qs = self._get_self_queryset().filter(*args, **kwargs)
        if not issubclass(qs.__class__, SoftDeleteQuerySet):
            qs.__class__ = SoftDeleteQuerySet
        return qs
    

class BaseModelAdmin(SimpleHistoryAdmin):
    """
    Classe d'administration personnalisée pour les modèles avec gestion de la suppression douce.

    Cette classe ajoute l'action de suppression douce à l'administration de modèle et
    configure le comportement de l'affichage des objets supprimés.
    
    """
    actions = [soft_delete]
    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget},
    }
    def get_queryset(self, request):
        """
        Retourne un queryset filtré pour exclure les objets supprimés.

        Args:
            request: La requête HTTP envoyée par l'utilisateur.

        Returns:
            QuerySet: QuerySet filtré pour exclure les objets supprimés.
        """
        qs = super(BaseModelAdmin, self).get_queryset(request)
        return qs.filter(deleted=False)
    
    def has_delete_permission(self, request, obj=None):
        """
        Désactive la permission de suppression pour les objets.

        Args:
            request: La requête HTTP envoyée par l'utilisateur.
            obj: L'objet à vérifier.

        Returns:
            bool: False pour désactiver la suppression.
        """
        return False
    def has_soft_delete_permission(self, request, obj=None):
        """
        Vérifie si l'utilisateur a la permission de réaliser une suppression douce.

        Args:
            request: La requête HTTP envoyée par l'utilisateur.
            obj: L'objet à vérifier.

        Returns:
            bool: True si l'utilisateur a la permission de suppression douce, sinon False.
        """
        opts = self.opts
        codename = get_permission_codename("soft_delete", opts)
        # print("%s.%s" % (opts.app_label, codename))
        return request.user.has_perm("%s.%s" % (opts.app_label, codename))
        

class SiteManager(models.Manager):
    def get_user_sites(self, user):
        """Retourne les sites accessibles à l'utilisateur"""
        if hasattr(user, 'reward_profile'):  
            return user.reward_profile.allowed_sites.all()
        return self.none()