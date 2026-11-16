from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from user_settings.models import UserSettings


class SalintoUserSettingsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='duartesettings',
            email='settings@salinto.ph',
            password='password123'
        )

    def test_settings_auto_created_signal(self):
        self.assertTrue(hasattr(self.user, 'settings'))
        self.assertTrue(self.user.settings.email_notifications)

    def test_settings_view(self):
        self.client.login(username='duartesettings', password='password123')
        response = self.client.get(reverse('user_settings:settings'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Notification Preferences')

    def test_toggle_notifications_view(self):
        self.client.login(username='duartesettings', password='password123')
        response = self.client.post(reverse('user_settings:toggle_notifications'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.user.settings.refresh_from_db()
        self.assertFalse(self.user.settings.email_notifications)
