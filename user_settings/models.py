from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserSettings(models.Model):
    """Preferences for a user, separate from their identity (User) or
    public-facing details (Profile)."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    email_notifications = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_settings_usersettings'
        verbose_name = 'User settings'
        verbose_name_plural = 'User settings'

    def __str__(self):
        return f"{self.user.username}'s settings"


@receiver(post_save, sender=User)
def create_or_update_user_settings(sender, instance, created, **kwargs):
    if created:
        UserSettings.objects.create(user=instance)
    else:
        if hasattr(instance, 'settings'):
            instance.settings.save()
