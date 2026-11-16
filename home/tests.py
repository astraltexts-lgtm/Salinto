from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import (
    Company,
    CompanyFollow,
    EmploymentType,
    Industry,
    Review,
    ReviewVote,
    SalaryEntry,
)


class SalintoHomeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testduarte',
            email='test@salinto.ph',
            password='password123'
        )
        self.industry = Industry.objects.create(name='Technology')
        self.etype = EmploymentType.objects.create(name='Direct hire')
        self.company = Company.objects.create(
            name='Test Corp PH',
            industry=self.industry,
            location='Taguig City',
        )
        self.company.employment_types.add(self.etype)

    def test_company_creation_and_attributes(self):
        self.assertEqual(str(self.company), 'Test Corp PH')
        self.assertEqual(self.company.rating, 0)
        self.assertEqual(self.company.review_count, 0)
        self.assertIn('Direct hire', self.company.employment_types_list())

    def test_review_recalculates_company_rating(self):
        review1 = Review.objects.create(
            user=self.user,
            company=self.company,
            rating=4,
            job_title='Software Engineer',
            comment='Great benefits.',
        )
        self.company.refresh_from_db()
        self.assertEqual(self.company.review_count, 1)
        self.assertEqual(float(self.company.rating), 4.0)

        # Another user review
        user2 = User.objects.create_user(username='reviewer2', password='password123')
        review2 = Review.objects.create(
            user=user2,
            company=self.company,
            rating=5,
            job_title='QA Engineer',
            comment='Superb culture.',
        )
        self.company.refresh_from_db()
        self.assertEqual(self.company.review_count, 2)
        self.assertEqual(float(self.company.rating), 4.5)

    def test_salary_entry_creation(self):
        salary = SalaryEntry.objects.create(
            company=self.company,
            submitted_by=self.user,
            employment_type=self.etype,
            job_title='DevOps Specialist',
            monthly_salary=Decimal('65000.00'),
        )
        self.assertEqual(salary.monthly_salary, Decimal('65000.00'))
        self.assertIn('DevOps Specialist', str(salary))

    def test_home_view_requires_login(self):
        response = self.client.get(reverse('home:home'))
        self.assertEqual(response.status_code, 302)

    def test_home_view_authenticated(self):
        self.client.login(username='testduarte', password='password123')
        response = self.client.get(reverse('home:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Corp PH')

    def test_company_detail_view(self):
        self.client.login(username='testduarte', password='password123')
        response = self.client.get(reverse('home:company_detail', args=[self.company.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Corp PH')
        self.assertContains(response, 'Write a Review')

    def test_toggle_follow_view(self):
        self.client.login(username='testduarte', password='password123')
        url = reverse('home:toggle_follow', args=[self.company.pk])
        
        # Follow
        res = self.client.post(url, follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(CompanyFollow.objects.filter(user=self.user, company=self.company).exists())

        # Unfollow
        res = self.client.post(url, follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertFalse(CompanyFollow.objects.filter(user=self.user, company=self.company).exists())
