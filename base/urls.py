from django.urls import path
from . import views

urlpatterns = [
    path('', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('edit/', views.edit_profile, name='edit_profile'),
    path('notifications/', views.list_notifications, name='list_notifications'),
    path('notifications/<int:notification_id>/mark-as-read/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('perimeter-autocomplete/', views.PerimeterAutocomplete.as_view(), name='perimeter-autocomplete',),

]