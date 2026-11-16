from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from profiles.models import Profile


class SalintoProfilesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='duarteprofile',
            email='duarte@salinto.ph',
            password='password123'
        )

    def test_profile_auto_created_signal(self):
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertEqual(self.user.profile.initials(), 'DU')

    def test_profile_view_authenticated(self):
        self.client.login(username='duarteprofile', password='password123')
        response = self.client.get(reverse('profiles:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'duarteprofile')

    def test_profile_edit_view(self):
        self.client.login(username='duarteprofile', password='password123')
        response = self.client.post(reverse('profiles:edit_profile'), {
            'display_name': 'Daniel Duarte Jr',
            'location': 'Metro Manila',
            'bio': 'Passionate builder & student.'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.display_name, 'Daniel Duarte Jr')
        self.assertEqual(self.user.profile.initials(), 'DJ')
