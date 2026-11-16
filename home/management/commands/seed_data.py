"""
Seed data script for Salinto.
Populates realistic Philippine companies, industries, employment types,
reviews, salary entries, profiles, and engagement data into Supabase PostgreSQL.
"""
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from home.models import (
    Industry,
    EmploymentType,
    Company,
    CompanyEmploymentType,
    Review,
    SalaryEntry,
    CompanyFollow,
    ReviewVote,
    ModerationFlag,
)
from profiles.models import Profile
from user_settings.models import UserSettings


class Command(BaseCommand):
    help = 'Seeds database with realistic Philippine workplace data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting Salinto database seed...'))

        # 1. Create or get test users
        users_data = [
            {
                'username': 'danielduarte',
                'email': 'daniel.duarte@salinto.ph',
                'first_name': 'Daniel',
                'last_name': 'Duarte Jr',
                'password': 'password123',
                'display_name': 'Daniel Duarte Jr',
                'location': 'Metro Manila, Philippines',
                'bio': 'Software engineering student & career researcher building Salinto.',
            },
            {
                'username': 'mariasantos',
                'email': 'maria.s@example.com',
                'first_name': 'Maria',
                'last_name': 'Santos',
                'password': 'password123',
                'display_name': 'Maria Santos',
                'location': 'Cebu City, Philippines',
                'bio': 'Senior Operations Associate with 6+ years in Cebu IT-BPM sector.',
            },
            {
                'username': 'juanreyes',
                'email': 'juan.r@example.com',
                'first_name': 'Juan',
                'last_name': 'Reyes',
                'password': 'password123',
                'display_name': 'Juan Reyes',
                'location': 'Quezon City, Philippines',
                'bio': 'Retail supervisor and workplace advocate.',
            },
            {
                'username': 'claramendoza',
                'email': 'clara.m@example.com',
                'first_name': 'Clara',
                'last_name': 'Mendoza',
                'password': 'password123',
                'display_name': 'Clara Mendoza',
                'location': 'Taguig City (BGC)',
                'bio': 'Full-stack cloud developer navigating PH tech salaries.',
            },
            {
                'username': 'admin',
                'email': 'admin@salinto.ph',
                'first_name': 'Salinto',
                'last_name': 'Admin',
                'password': 'adminpassword123',
                'is_staff': True,
                'is_superuser': True,
                'display_name': 'Platform Moderator',
                'location': 'Manila',
                'bio': 'Official Salinto administrator and review moderation desk.',
            },
        ]

        created_users = {}
        for udata in users_data:
            user, created = User.objects.get_or_create(
                username=udata['username'],
                defaults={
                    'email': udata['email'],
                    'first_name': udata.get('first_name', ''),
                    'last_name': udata.get('last_name', ''),
                    'is_staff': udata.get('is_staff', False),
                    'is_superuser': udata.get('is_superuser', False),
                }
            )
            if created or not user.has_usable_password():
                user.set_password(udata['password'])
                user.save()

            # Ensure profile exists
            profile, _ = Profile.objects.get_or_create(
                user=user,
                defaults={
                    'display_name': udata.get('display_name', user.username),
                    'location': udata.get('location', ''),
                    'bio': udata.get('bio', ''),
                }
            )
            # Ensure settings exist
            UserSettings.objects.get_or_create(user=user, defaults={'email_notifications': True})
            created_users[udata['username']] = user
            self.stdout.write(f"  User ready: {user.username}")

        # 2. Industries
        industries_list = [
            'Business Process Outsourcing',
            'Information Technology',
            'Financial Services',
            'Retail & E-Commerce',
            'Logistics & Freight',
            'Agriculture',
            'Healthcare',
            'Telecommunications',
            'Renewable Energy',
        ]
        created_industries = {}
        for ind_name in industries_list:
            ind, _ = Industry.objects.get_or_create(name=ind_name)
            created_industries[ind_name] = ind

        # 3. Employment Types
        employment_types_list = [
            'Direct hire',
            'Agency hired',
            'Project based',
            'Night differential',
            'Hybrid / Remote',
            'Seasonal',
        ]
        created_etypes = {}
        for et_name in employment_types_list:
            et, _ = EmploymentType.objects.get_or_create(name=et_name)
            created_etypes[et_name] = et

        # 4. Companies
        companies_data = [
            {
                'name': 'Bayanihan BPO Solutions',
                'industry': created_industries['Business Process Outsourcing'],
                'location': 'Cebu City',
                'etypes': ['Direct hire', 'Night differential', 'Hybrid / Remote'],
            },
            {
                'name': 'Lantawan Agri Corp',
                'industry': created_industries['Agriculture'],
                'location': 'Davao del Sur',
                'etypes': ['Direct hire', 'Seasonal'],
            },
            {
                'name': 'Tahanan Retail Group',
                'industry': created_industries['Retail & E-Commerce'],
                'location': 'Quezon City',
                'etypes': ['Agency hired', 'Project based'],
            },
            {
                'name': 'Marino Logistics PH',
                'industry': created_industries['Logistics & Freight'],
                'location': 'Iloilo City',
                'etypes': ['Direct hire', 'Project based'],
            },
            {
                'name': 'Maynilad Cloud Innovations',
                'industry': created_industries['Information Technology'],
                'location': 'Taguig City (BGC)',
                'etypes': ['Direct hire', 'Hybrid / Remote'],
            },
            {
                'name': 'Archipelago Fintech Systems',
                'industry': created_industries['Financial Services'],
                'location': 'Makati City',
                'etypes': ['Direct hire', 'Hybrid / Remote'],
            },
            {
                'name': 'Horizon Health Philippines',
                'industry': created_industries['Healthcare'],
                'location': 'Pasig City',
                'etypes': ['Direct hire', 'Night differential'],
            },
            {
                'name': 'Bagong Araw Renewable Energy',
                'industry': created_industries['Renewable Energy'],
                'location': 'Batangas City',
                'etypes': ['Direct hire', 'Project based'],
            },
        ]

        created_companies = {}
        for cdata in companies_data:
            company, created = Company.objects.get_or_create(
                name=cdata['name'],
                defaults={
                    'industry': cdata['industry'],
                    'location': cdata['location'],
                }
            )
            # Add company employment types
            for et_name in cdata['etypes']:
                et = created_etypes[et_name]
                CompanyEmploymentType.objects.get_or_create(company=company, employment_type=et)

            created_companies[cdata['name']] = company

        # 5. Reviews
        reviews_data = [
            {
                'user': created_users['mariasantos'],
                'company': created_companies['Bayanihan BPO Solutions'],
                'employment_type': created_etypes['Night differential'],
                'rating': 4,
                'job_title': 'Customer Care Specialist',
                'comment': 'Good health benefits with Maxicare HMO day 1. Night differential pay is consistently on time. Team managers are approachable, though peak season queues can be high pressure.',
            },
            {
                'user': created_users['danielduarte'],
                'company': created_companies['Bayanihan BPO Solutions'],
                'employment_type': created_etypes['Direct hire'],
                'rating': 5,
                'job_title': 'Quality Assurance Analyst',
                'comment': 'Transparent performance metrics and very clean facilities in Cebu IT Park. Career progression ladder is well-defined.',
            },
            {
                'user': created_users['juanreyes'],
                'company': created_companies['Tahanan Retail Group'],
                'employment_type': created_etypes['Agency hired'],
                'rating': 3,
                'job_title': 'Floor Sales Associate',
                'comment': 'Pay is standard minimum wage with incentives, but long standing hours during mall sales. Agency deductions should be more transparent.',
            },
            {
                'user': created_users['claramendoza'],
                'company': created_companies['Maynilad Cloud Innovations'],
                'employment_type': created_etypes['Hybrid / Remote'],
                'rating': 5,
                'job_title': 'Senior Software Engineer',
                'comment': 'Exceptional engineering culture. Modern tech stack (Python, Django, Postgres, AWS), flexible hybrid arrangement (2 days office in BGC), and continuous learning budget.',
            },
            {
                'user': created_users['mariasantos'],
                'company': created_companies['Maynilad Cloud Innovations'],
                'employment_type': created_etypes['Direct hire'],
                'rating': 4,
                'job_title': 'Product Manager',
                'comment': 'Collaborative product squads and competitive compensation package. Rapid release cycles keep teams energized.',
            },
            {
                'user': created_users['juanreyes'],
                'company': created_companies['Marino Logistics PH'],
                'employment_type': created_etypes['Direct hire'],
                'rating': 5,
                'job_title': 'Logistics Operations Lead',
                'comment': 'Reliable shipping schedules and supportive operations leadership across Western Visayas branches. Fair overtime compensation.',
            },
            {
                'user': created_users['danielduarte'],
                'company': created_companies['Lantawan Agri Corp'],
                'employment_type': created_etypes['Direct hire'],
                'rating': 4,
                'job_title': 'Agronomy Field Officer',
                'comment': 'Sustainable farming practices in Mindanao. Field per diem and hazard allowances provided promptly.',
            },
            {
                'user': created_users['claramendoza'],
                'company': created_companies['Archipelago Fintech Systems'],
                'employment_type': created_etypes['Direct hire'],
                'rating': 4,
                'job_title': 'Backend Developer',
                'comment': 'Fast-paced fintech environment with high volume microservices. 14th-month bonus and wellness allowance are great perks.',
            },
            {
                'user': created_users['mariasantos'],
                'company': created_companies['Horizon Health Philippines'],
                'employment_type': created_etypes['Direct hire'],
                'rating': 4,
                'job_title': 'Clinical Document Specialist',
                'comment': 'Comprehensive HMO covering 2 dependents from day 1. Stable medical BPO account with supportive nurse leads.',
            },
        ]

        created_reviews = []
        for rdata in reviews_data:
            review, created = Review.objects.get_or_create(
                user=rdata['user'],
                company=rdata['company'],
                job_title=rdata['job_title'],
                defaults={
                    'employment_type': rdata['employment_type'],
                    'rating': rdata['rating'],
                    'comment': rdata['comment'],
                }
            )
            created_reviews.append(review)
            review.company.update_rating_and_count()

        # 6. Salary Entries
        salaries_data = [
            {
                'company': created_companies['Bayanihan BPO Solutions'],
                'submitted_by': created_users['mariasantos'],
                'employment_type': created_etypes['Night differential'],
                'job_title': 'Customer Care Specialist',
                'monthly_salary': Decimal('28500.00'),
            },
            {
                'company': created_companies['Bayanihan BPO Solutions'],
                'submitted_by': created_users['danielduarte'],
                'employment_type': created_etypes['Direct hire'],
                'job_title': 'Quality Assurance Analyst',
                'monthly_salary': Decimal('36000.00'),
            },
            {
                'company': created_companies['Bayanihan BPO Solutions'],
                'submitted_by': None,  # Anonymous
                'employment_type': created_etypes['Direct hire'],
                'job_title': 'Team Leader - Operations',
                'monthly_salary': Decimal('48000.00'),
            },
            {
                'company': created_companies['Maynilad Cloud Innovations'],
                'submitted_by': created_users['claramendoza'],
                'employment_type': created_etypes['Hybrid / Remote'],
                'job_title': 'Senior Software Engineer',
                'monthly_salary': Decimal('115000.00'),
            },
            {
                'company': created_companies['Maynilad Cloud Innovations'],
                'submitted_by': created_users['mariasantos'],
                'employment_type': created_etypes['Direct hire'],
                'job_title': 'Product Manager',
                'monthly_salary': Decimal('95000.00'),
            },
            {
                'company': created_companies['Maynilad Cloud Innovations'],
                'submitted_by': None,
                'employment_type': created_etypes['Hybrid / Remote'],
                'job_title': 'Junior Full Stack Engineer',
                'monthly_salary': Decimal('45000.00'),
            },
            {
                'company': created_companies['Tahanan Retail Group'],
                'submitted_by': created_users['juanreyes'],
                'employment_type': created_etypes['Agency hired'],
                'job_title': 'Floor Sales Associate',
                'monthly_salary': Decimal('18500.00'),
            },
            {
                'company': created_companies['Marino Logistics PH'],
                'submitted_by': created_users['juanreyes'],
                'employment_type': created_etypes['Direct hire'],
                'job_title': 'Logistics Operations Lead',
                'monthly_salary': Decimal('42000.00'),
            },
            {
                'company': created_companies['Archipelago Fintech Systems'],
                'submitted_by': created_users['claramendoza'],
                'employment_type': created_etypes['Direct hire'],
                'job_title': 'Backend Developer',
                'monthly_salary': Decimal('85000.00'),
            },
            {
                'company': created_companies['Lantawan Agri Corp'],
                'submitted_by': created_users['danielduarte'],
                'employment_type': created_etypes['Direct hire'],
                'job_title': 'Agronomy Field Officer',
                'monthly_salary': Decimal('32000.00'),
            },
        ]

        for sdata in salaries_data:
            SalaryEntry.objects.get_or_create(
                company=sdata['company'],
                job_title=sdata['job_title'],
                monthly_salary=sdata['monthly_salary'],
                defaults={
                    'submitted_by': sdata['submitted_by'],
                    'employment_type': sdata['employment_type'],
                }
            )

        # 7. Company Follows
        CompanyFollow.objects.get_or_create(
            user=created_users['danielduarte'],
            company=created_companies['Maynilad Cloud Innovations'],
        )
        CompanyFollow.objects.get_or_create(
            user=created_users['danielduarte'],
            company=created_companies['Bayanihan BPO Solutions'],
        )
        CompanyFollow.objects.get_or_create(
            user=created_users['mariasantos'],
            company=created_companies['Bayanihan BPO Solutions'],
        )

        # 8. Review Votes
        if created_reviews:
            ReviewVote.objects.get_or_create(
                user=created_users['danielduarte'],
                review=created_reviews[0],
                defaults={'is_helpful': True},
            )
            ReviewVote.objects.get_or_create(
                user=created_users['claramendoza'],
                review=created_reviews[0],
                defaults={'is_helpful': True},
            )

        # 9. Moderation Flag (demonstrating moderation capability)
        if len(created_reviews) > 2:
            ModerationFlag.objects.get_or_create(
                review=created_reviews[2],
                reported_by=created_users['claramendoza'],
                defaults={
                    'reason': 'Please verify accuracy of agency deductions mentioned.',
                    'status': ModerationFlag.STATUS_PENDING,
                }
            )

        self.stdout.write(self.style.SUCCESS(
            f"Successfully seeded: {Company.objects.count()} companies, "
            f"{Review.objects.count()} reviews, {SalaryEntry.objects.count()} salaries, "
            f"{Industry.objects.count()} industries into Supabase PostgreSQL!"
        ))
