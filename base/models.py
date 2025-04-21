from django.contrib.auth.models import UserManager, AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from simple_history.models import HistoricalRecords
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.tokens import default_token_generator

from django.utils import timezone
from django.conf import settings
from tree_queries.models import TreeNode
from django.db import models
from .managers import BaseModelManager, SiteManager

""" Customisation des models UserManager , User et ........"""

class AbstractBaseModel(models.Model):
    """
    Modèle de base abstrait contenant des champs communs pour tous les modèles.
    - `created_at` : Date de création de l'instance.
    - `updated_at` : Date de dernière mise à jour de l'instance.
    - `deleted` : Indique si l'instance est marquée comme supprimée (soft delete).

    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    objects = BaseModelManager()
    
    class Meta:
        abstract = True
        default_permissions = ['add', 'change', 'view', "soft_delete"]
      
    def soft_delete(self):
        """
        Marque l'instance comme supprimée tout en vérifiant si elle est référencée
        par d'autres objets non supprimés. Lève une ValidationError si c'est le cas.
        """
        # Get the classes that reference self that are instances of BaseModel and are not soft deleted
        for f in self._meta.get_fields():
            if f.one_to_many or f.one_to_one:
                if  issubclass(f.related_model, AbstractBaseModel) and \
                        f.related_model.objects.filter(**{f.field.name: self}, deleted=False).exists() :
                    raise ValidationError("Vous ne pouvez pas supprimer cet élément car il est référencé par au moins un élément de type {0}".format(f.related_model._meta.verbose_name))
        self.deleted = True
        self.save()
          
    def delete(self):
        """
        Surcharge de la méthode `delete` pour utiliser la suppression logique (soft delete).
        """
        return self.soft_delete()
        
    def save(self, *args, **kwargs):
        """
        Surcharge de la méthode `save` pour empêcher la suppression d'un objet
        non encore enregistré dans la base de données.
        """
        if self.deleted and not self.pk:
            raise ValidationError("Vous ne pouvez pas supprimer un objet qui n'est pas encore enregistré.")
        super(AbstractBaseModel, self).save(*args, **kwargs)


class CustomUserManager(UserManager):

    def create_user(self, email, password=None, is_superuser = False, is_member=False, is_helpdesk = False, is_manager = False ):
        
        if not email:
            raise ValueError("L'email est obligatoire.")

        user = self.model(email=self.normalize_email(email), is_superuser=is_superuser, is_member=is_member, is_helpdesk=is_helpdesk, is_manager=is_manager)

        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password):
        
        user = self.create_user(
            email=email,
            password=password,
            is_staff=True,
            is_superuser=True
        )


""" Creation des models Company, Site , Perimetre ........"""

class Company(AbstractBaseModel):
    
    class CompanyForms(models.TextChoices):
        SARL = 'sarl', 'SARL'
        SARLAU = 'sarlau', 'SARL AU'
        SA = 'sa', 'SA'
    name = models.CharField(max_length = 30, verbose_name = "Raison sociale")
    phone = models.CharField(max_length = 16, verbose_name = "Téléphone",null = True, blank = True)
    address1 = models.CharField(max_length =30, verbose_name = "Adresse",null = True, blank = True)
    address2 = models.CharField(max_length =30, verbose_name = "Suite",null = True, blank = True)
    city = models.CharField(max_length =15, verbose_name = "Ville")
    licence = models.CharField(max_length =15, verbose_name = "Patente",null = True, blank = True)
    registration_id = models.CharField(max_length =15, verbose_name = "Registre de commerce",null = True, blank = True)
    social_id = models.CharField(max_length =15, verbose_name = "Num CNSS",null = True, blank = True)
    tax_id = models.CharField(max_length =15, verbose_name = "Identifiant fiscal",null = True, blank = True)
    company_id = models.CharField(max_length =15, verbose_name = "ICE",null = True, blank = True)
    company_form = models.CharField(max_length = 10, verbose_name = "Forme juridique",choices=CompanyForms.choices,null = True, blank = True)
    logo = models.ImageField(upload_to='logo',blank=True,null=True, verbose_name = "Logo")
    history = HistoricalRecords(table_name="base_company_history")
        
    class Meta(AbstractBaseModel.Meta):
        ordering = ["name"]
        verbose_name = "Société"
        verbose_name_plural = "Sociétés"
        permissions = ()
        db_table = "base_company"

    def __str__(self):
        if self.company_form:
            return "{0} {1}".format(self.name, self.get_company_form_display())
        else:
            return self.name

class Regions(models.TextChoices):
    """
    Enumération des régions du Maroc.
    Contient des codes et noms pour chaque région.
    """
    MA01 = "MA01", "Tanger-Tétouan-Al Hoceïma"
    MA02 = "MA02", "L'Oriental"
    MA03 = "MA03", "Fès-Meknès"
    MA04 = "MA04", "Rabat-Salé-Kénitra"
    MA05 = "MA05", "Béni Mellal-Khénifra"
    MA06 = "MA06", "Casablanca-Settat"
    MA07 = "MA07", "Marrakech-Safi"
    MA08 = "MA08", "Drâa-Tafilalet"
    MA09 = "MA09", "Souss-Massa"
    MA10 = "MA10", "Guelmim-Oued Noun"
    MA11 = "MA11", "Laâyoune-Sakia El Hamra"
    MA12 = "MA12", "Dakhla-Oued Ed-Dahab"
    ATRE = "ATRE", "Autre / Etranger"


# MinValueValidator and MaxValueValidator are used to validate the longitude 
if hasattr(settings, "LONGITUDE_MIN_MAX"):
    min_long, max_long = settings.LONGITUDE_MIN_MAX
    longitude_validators = [
        MinValueValidator(min_long),
        MaxValueValidator(max_long)
    ]
else: 
    longitude_validators = [
        MinValueValidator(-180),
        MaxValueValidator(180)
    ]
if hasattr(settings, "LATITUDE_MIN_MAX"):
    min_lat, max_lat = settings.LATITUDE_MIN_MAX
    latitude_validators = [
        MinValueValidator(min_lat),
        MaxValueValidator(max_lat)
    ]
else:
    latitude_validators = [
        MinValueValidator(-90),
        MaxValueValidator(90)
    ]

class Site(AbstractBaseModel):
    
    name = models.CharField(max_length = 30, verbose_name = "Nom")
    location = models.CharField(max_length=255, blank=True, null=True)
    qr_code_identifier = models.CharField(max_length=100, unique=True, blank=True, null=True)  # Identifiant unique pour le QR code
    is_active = models.BooleanField(default=True)
    phone = models.CharField(max_length = 16, verbose_name = "Téléphone",null = True, blank = True)
    address1 = models.CharField(max_length =30, verbose_name = "Adresse",null = True, blank = True)
    address2 = models.CharField(max_length =30, verbose_name = "Suite",null = True, blank = True)
    city = models.CharField(max_length =15, verbose_name = "Ville",null = True, blank = True)
    reference = models.CharField(max_length =5, verbose_name = "Ref",unique = True)
    longitude = models.FloatField(verbose_name = "Longitude", validators=longitude_validators)
    latitude = models.FloatField(verbose_name = "Latitude", validators=latitude_validators)
    stamp_rate = models.DecimalField(verbose_name = "Taux de droits de timbre (%)", default = 0,
                    validators=[MinValueValidator(0),MaxValueValidator(100)]  , help_text="Entre 0 et 100", max_digits=6, decimal_places=3)
    company = models.ForeignKey(Company, verbose_name = "Société",related_name="sites",on_delete=models.PROTECT )
    region = models.CharField(max_length = 6, verbose_name = "Région",choices=Regions.choices)
    history = HistoricalRecords(table_name="base_site_history")

    objects = SiteManager()
        
    class Meta(AbstractBaseModel.Meta):
        ordering = ["name"]
        verbose_name = "Site"
        verbose_name_plural = "Sites"
        permissions = ()
        db_table = "base_site"
        
    def generate_qr_code_data(self):
        token = default_token_generator.make_token(self)
        return f"incident:{self.id}:{token}"
        
    def __str__(self):
        return self.name
    
    def clean(self):
        """
        Validation des données du site avant enregistrement.
        """
        super().clean()  

        if len(self.reference) != 5:
            raise ValidationError({'reference': 'La référence doit contenir exactement 5 caractères.'})

        if self.longitude is not None and (self.longitude < -180 or self.longitude > 180):
            raise ValidationError({'longitude': 'La longitude doit être comprise entre -180 et 180.'})

        if self.latitude is not None and (self.latitude < -90 or self.latitude > 90):
            raise ValidationError({'latitude': 'La latitude doit être comprise entre -90 et 90.'})

        if self.stamp_rate < 0 or self.stamp_rate > 100:
            raise ValidationError({'stamp_rate': 'Le taux de droits de timbre doit être compris entre 0 et 100.'})

        if self.region not in dict(Regions.choices).keys():
            raise ValidationError({'region': 'La région sélectionnée n\'est pas valide.'})

        if self.phone and not self.phone.isdigit():
            raise ValidationError({'phone': 'Le numéro de téléphone ne doit contenir que des chiffres.'})

        if self.address1 and len(self.address1) > 30:
            raise ValidationError({'address1': 'L\'adresse ne doit pas dépasser 30 caractères.'})

        if self.address2 and len(self.address2) > 30:
            raise ValidationError({'address2': 'La suite de l\'adresse ne doit pas dépasser 30 caractères.'})

        if self.city and len(self.city) > 15:
            raise ValidationError({'city': 'Le nom de la ville ne doit pas dépasser 15 caractères.'})


class Emplacement(AbstractBaseModel):
    class Meta:
        verbose_name = "Emplacement de travail"
        verbose_name_plural = "Emplacements de travail"
        ordering = ['site', 'name']
    
    name = models.CharField(max_length=255, verbose_name="Nom de l'emplacement")
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='emplacements')
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} ({self.site.name})"
     
class User(AbstractUser, AbstractBaseModel):

    ROLE_CHOICES = [
        ("technicien", "Technicien"),
        ("gestionnaire", "Gestionnaire"),
        ("livreur", "Livreur"),
        ("vendeur", "Vendeur"),
    ]
    
    username = models.CharField(max_length=150, default = "deprecated", unique=False, null=True, blank=True)
    email = models.EmailField(verbose_name = 'Adresse email', unique=True, null=False, blank=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name = "Numéro de téléphone")
    objects = CustomUserManager()
    first_name= models.CharField(max_length=30, blank=True)
    last_name= models.CharField(max_length=30, blank=True)
    adresse = models.CharField(max_length=30, blank=True)
    company = models.CharField( max_length=30, null=True, blank=True, verbose_name = "Société")
    is_internal = models.BooleanField(default=False, verbose_name = "Utilisateur interne ?",
                                        help_text="Cocher si l'utilisateur est un employé de la société.", blank=True)
    welcome_email_to_send = models.BooleanField(default=True, verbose_name = "Envoyer un email de bienvenue?",
                                help_text="L'email ne sera envoyé que si des comptes ou des périmètres sont associés à l'utilisateur")
    welcome_email_sent = models.BooleanField(default=False, verbose_name = "Email de bienvenue envoyé?")
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default="technicien",
        verbose_name="Type d'utilisateur",
        blank=True
    )
    perimeters = models.ManyToManyField('Perimeter', through='UserPerimeterRel', related_name="users", verbose_name = "Périmètres", blank=True)
    photo = models.ImageField(upload_to='profile_img', blank=True, verbose_name = "photo de profil")
    history = HistoricalRecords(table_name="base_user_history")

    
    class Meta(AbstractBaseModel.Meta):
        verbose_name = ('Utilisateur')
        verbose_name_plural = ('Utilisateurs')
        db_table = "base_user"
        
    def __str__(self):
        return self.get_full_name() if self.get_full_name() else self.email

    def save(self, *args, **kwargs):
        """
        Sauvegarde l'utilisateur.
        """
        self.full_clean() 
        super().save(*args, **kwargs)

    @property
    def get_last_notificaitons(self):
        return self.notifications.order_by("-created_at")[:10]
    
    @property
    def unread_notifications_count(self):
        """
        Retourne le nombre de notifications non lues.
        """
        nb = self.notifications.filter(read_at__isnull=True).count()
        if nb == 0:
            return ""
        return str(nb) if nb <= 99 else "99+"



class PerimeterCategory(AbstractBaseModel):
   
    class Meta:
        db_table = "base_perimeter_category"
        verbose_name = ('Catégorie de périmètres')
        verbose_name_plural = ('Catégories de périmètres')
        ordering = ['name']
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=100, verbose_name = "Nom")
    description = models.TextField(blank=True, verbose_name = "Description")
    history = HistoricalRecords(table_name="base_perimeter_category_history")
    
    def __str__(self):
        return self.name


class Perimeter(TreeNode, AbstractBaseModel):
    """
    Représente un périmètre dans la hiérarchie des périmètres.

    Attributes:
        created_at (datetime): Date de création du périmètre.
        updated_at (datetime): Date de dernière modification du périmètre.
        name (str): Nom du périmètre.
        external_id (str): Référence externe unique du périmètre.
        display_order (int): Ordre d'affichage du périmètre.
        description (str): Description du périmètre.
        site (Site): Référence au site associé au périmètre.
        category (PerimeterCategory): Catégorie du périmètre.
        history (HistoricalRecords): Historique des modifications du périmètre.
    """
    class Meta:
        verbose_name = ('Périmètre')
        verbose_name_plural = ('Périmètres')
        db_table = "base_perimeter"
        ordering = ['display_order', ]
        unique_together = ('display_order', 'site')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=100, verbose_name = "Nom")
    external_id = models.CharField(max_length=12, verbose_name = "Référence")
    display_order = models.PositiveIntegerField(default = 100, verbose_name = "Ordre d'affichage")
    description = models.TextField(blank=True, verbose_name = "Description")
    site = models.ForeignKey('Site', on_delete=models.CASCADE, verbose_name = "Site", related_name="perimeters", null=True, blank=True)
    category = models.ForeignKey(PerimeterCategory, on_delete=models.PROTECT, verbose_name = "Catégorie", null=True, blank=True)
    history = HistoricalRecords(table_name="base_perimeter_history")
    
    def __str__(self):
        return "[{0}] {1}".format(self.external_id , self.name)
    
    @property
    def tree_label(self):
        """
        Génère une représentation textuelle du périmètre avec son niveau dans l'arborescence.

        Returns:
            str: Étiquette arborescente du périmètre.
        """
        depth = getattr(self, "tree_depth", 0)      
        return "{}{}".format("".join(["--- "] * depth), self)
    
    def clean(self):        
        if self.parent and self.site and self.parent.site and self.site != self.parent.site :
            raise ValidationError({"site": 'Le site ne correspond pas au site de son parent'})
        if self.parent and self.parent.site and not self.site:
            raise ValidationError({"site": 'Le site ne correspond pas au site de son parent'})
        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class UserPerimeterRel(models.Model):
    """
    Relation entre un utilisateur et un périmètre, avec des préférences de notification.

    Attributes:
        user (User): Référence à l'utilisateur.
        perimeter (Perimeter): Référence au périmètre.
        email_notify_new_order (bool): Notification par email des nouvelles commandes.
        email_notify_new_ticket (bool): Notification par email des nouveaux tickets.
        web_notifications (bool): Activation des notifications web.
        assign_tickets (bool): Indique si l'utilisateur est responsable de l'assignation des tickets.
        history (HistoricalRecords): Historique des modifications.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="perimeter_rels", verbose_name = "Utilisateur")
    perimeter = models.ForeignKey(Perimeter, on_delete=models.CASCADE, related_name="user_rels", verbose_name = "Périmètre")
    email_notify_new_order = models.BooleanField(default=True, verbose_name = "Notifier les nouvelles incidents par email")
    email_notify_new_ticket = models.BooleanField(default=True, verbose_name = "Notifier les nouveaux tickets par email")
    web_notifications = models.BooleanField(default=True, verbose_name = "Notifications web")
    assign_tickets = models.BooleanField(default=True, verbose_name = "Assigner des tickets",
                                        help_text="Un seul utilisateur peut être associé à un périmètre pour l'assignation des tickets")
    history = HistoricalRecords(table_name="base_user_perimeter_rel_history")
    
    class Meta:
        db_table = "base_user_perimeter_rel"
        verbose_name = ('Relation Utilisateur - Périmètre')
        verbose_name_plural = ('Relations Utilisateur - Périmètre')
        unique_together = ('user', 'perimeter')
        constraints = [
            models.UniqueConstraint(fields=["perimeter", "assign_tickets"], condition=models.Q(assign_tickets=True), name="unique_perimeter_assign_tickets")
        ]
        
    def __str__(self):
        return "{0} - {1}".format(self.user, self.perimeter)
    
    def clean(self):
        """
        Valide les contraintes sur la relation utilisateur - périmètre.

        Raises:
            ValidationError: Si un utilisateur externe est assigné ou si un conflit existe.
        """
        if not self.user.is_internal:
            raise ValidationError("Un utilisateur externe ne peut pas être associé à un périmètre")
        if self.assign_tickets and \
                UserPerimeterRel.objects.filter(assign_tickets = True, perimeter=self.perimeter).exclude(pk=self.pk).exists():
            previous_rel = UserPerimeterRel.objects.filter(assign_tickets = True, perimeter=self.perimeter).exclude(pk=self.pk).first()
            raise ValidationError("un utilisateur est déjà associé à ce périmètre pour l'assignation des tickets: {0}".format(previous_rel.user))
        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Notification(models.Model):
    """
    Représente une notification envoyée à un utilisateur.

    Attributes:
        created_at (datetime): Date et heure de création de la notification.
        read_at (datetime): Date et heure où la notification a été lue.
        user (User): Référence à l'utilisateur destinataire de la notification.
        title (str): Titre de la notification.
        message (str): Contenu de la notification.
        content_type (ContentType): Type de contenu lié à la notification.
        object_id (int): Identifiant de l'objet associé au type de contenu.
        content_object (GenericForeignKey): Référence générique à l'objet associé.
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name = "Date de création")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name = "Lu le")
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="notifications", verbose_name = "Utilisateur")
    title = models.CharField(max_length=100, verbose_name = "Titre")
    message = models.CharField(max_length=500, verbose_name = "Message")
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.PROTECT, null=True, blank=True, verbose_name="Type de contenu")
    object_id = models.PositiveIntegerField(verbose_name = "ID de l'objet", null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")
    
    
    class Meta:
        db_table = "base_notification"
        verbose_name = ('Notification')
        verbose_name_plural = ('Notifications')

    def __str__(self):
        return self.message[:50] + "..." if len(self.message) > 50 else self.message

