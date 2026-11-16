from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """
    Extra profile information for a user, beyond what Django's built-in
    User model stores (username, email, password).
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    display_name = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    bio = models.CharField(max_length=280, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'profile_profile'

    def __str__(self):
        return f"{self.user.username}'s profile"

    def display_label(self):
        return self.display_name or self.user.username

    def initials(self):
        label = self.display_label().strip()
        if not label:
            return '?'
        parts = label.split()
        if len(parts) == 1:
            return parts[0][:2].upper()
        return (parts[0][0] + parts[-1][0]).upper()


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
