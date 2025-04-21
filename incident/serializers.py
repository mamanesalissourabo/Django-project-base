# from rest_framework import serializers
# from incident.models import Incident
# from django.contrib.auth import get_user_model

# User = get_user_model()

# class QalitasIncidentSerializer(serializers.ModelSerializer):
#     # Champs de base obligatoires
#     type_incident = serializers.CharField(source='get_type_incident_display')
#     site = serializers.CharField(source='site.name', allow_null=True)
#     created_by = serializers.SerializerMethodField()
    
#     # Champs conditionnels selon le type d'incident
#     pa_fields = serializers.SerializerMethodField()
#     ose_fields = serializers.SerializerMethodField()

#     class Meta:
#         model = Incident
#         fields = [
#             'reference',
#             'name',
#             'report_date',
#             'description',
#             'location',
#             'type_incident',
#             'site',
#             'created_by',
#             'pa_fields',
#             'ose_fields',
#             'photo_url'
#         ]
#         read_only_fields = ['reference', 'report_date']

#     def get_created_by(self, obj):
#         if obj.created_by_user:
#             return {
#                 'id': obj.created_by_user.id,
#                 'name': obj.created_by_user.get_full_name(),
#                 'email': obj.created_by_user.email
#             }
#         return None

#     def get_pa_fields(self, obj):
#         if obj.type_incident == 'PA':
#             return {
#                 'blessure_potentielle': obj.blessure_potentielle,
#                 'cause_principale': obj.cause_principale,
#                 'consequence_pa': obj.consequence_pa,
#                 'solution_pa': obj.solution_pa
#             }
#         return None

#     def get_ose_fields(self, obj):
#         if obj.type_incident == 'OSE':
#             return {
#                 'consequence_ose': obj.consequence_ose,
#                 'solution_ose': obj.solution_ose,
#                 'action_correction': obj.action_correction,
#                 'commentaire_correction': obj.commentaire_correction,
#                 'photo_correction_url': self.get_photo_url(obj.photo_correction) if obj.photo_correction else None
#             }
#         return None

#     def get_photo_url(self, photo):
#         if photo:
#             return self.context['request'].build_absolute_uri(photo.url)
#         return None

#     def to_representation(self, instance):
#         """Transforme l'instance en dictionnaire pour la sérialisation"""
#         data = super().to_representation(instance)
        
#         # Nettoyage des champs null
#         for field in list(data.keys()):
#             if data[field] is None:
#                 del data[field]
                
#         return data