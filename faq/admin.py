from django.contrib import admin

from faq.models import FAQ, FAQCategory
from .models import SupportTicket

admin.site.register(FAQ)
admin.site.register(FAQCategory)

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'first_name', 'last_name', 'email', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'first_name', 'last_name', 'email', 'message')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Contenu du ticket', {
            'fields': ('title', 'message')
        }),
        ('Métadonnées', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )