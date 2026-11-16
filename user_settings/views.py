from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .models import UserSettings


@login_required(login_url='login:login')
def settings_view(request):
    """Displays user preferences and notifications settings."""
    settings_obj, _ = UserSettings.objects.get_or_create(user=request.user)
    return render(request, 'user_settings/settings.html', {'settings': settings_obj})


@login_required(login_url='login:login')
@require_POST
def toggle_notifications_view(request):
    """Toggles email notifications preference."""
    settings_obj, _ = UserSettings.objects.get_or_create(user=request.user)
    settings_obj.email_notifications = not settings_obj.email_notifications
    settings_obj.save()

    status = "enabled" if settings_obj.email_notifications else "disabled"
    messages.success(request, f'Email notification alerts have been {status}.')
    return redirect('user_settings:settings')
