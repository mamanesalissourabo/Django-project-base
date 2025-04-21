from django.contrib import admin

from incident.models import Incident

class IncidentAdmin(admin.ModelAdmin):
    list_display = ('reference', 'name', 'type_incident', 'status', 'report_date', 'site')
    list_filter = ('type_incident', 'status', 'site', 'report_date')
    search_fields = ('reference', 'name', 'description')
    readonly_fields = ('reference', 'report_date', 'updated_at', 'created_by_user', 'updated_by_user')
    fieldsets = (
        ('Informations de base', {
            'fields': (
                'reference', 
                'name', 
                'type_incident',
                'description',
                'status',
            )
        }),
        ('Localisation', {
            'fields': (
                'site',
                'emplacement',
                'location'
            )
        }),
        ('Photos', {
            'fields': (
                'photo',
                'photo_correction'
            )
        }),
        ('Détails PA', {
            'fields': (
                'blessure_potentielle',
                'cause_principale',
                'consequence_pa',
                'solution_pa'
            ),
            'classes': ('collapse',)
        }),
        ('Détails OSE', {
            'fields': (
                'consequence_ose',
                'solution_ose'
            ),
            'classes': ('collapse',)
        }),
        ('Correction immédiate', {
            'fields': (
                'action_correction',
                'commentaire_correction'
            )
        }),
        ('Métadonnées', {
            'fields': (
                'report_date',
                'updated_at',
                'created_by_user',
                'updated_by_user',
                'assigned_to'
            ),
            'classes': ('collapse',)
        }),
        ('Commentaires', {
            'fields': ('comment',)
        })
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by_user = request.user
        obj.updated_by_user = request.user
        super().save_model(request, obj, form, change)

admin.site.register(Incident, IncidentAdmin)
