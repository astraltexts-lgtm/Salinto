from django.urls import path

from . import views

app_name = 'user_settings'

urlpatterns = [
    path('settings/', views.settings_view, name='settings'),
    path('settings/toggle-notifications/', views.toggle_notifications_view, name='toggle_notifications'),
]
