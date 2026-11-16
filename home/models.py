from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


# ── Lookup tables ──────────────────────────────────────────────────────────

class Industry(models.Model):
    """e.g. 'Business Process Outsourcing', 'Retail'. One canonical row per
    industry so filters never treat 'BPO' and 'Business Process Outsourcing'
    as different things."""

    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'industry'
        ordering = ['name']
        verbose_name_plural = 'industries'

    def __str__(self):
        return self.name


class EmploymentType(models.Model):
    """e.g. 'Direct hire', 'Agency hired', 'Project based'."""

    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'employment_type'
        ordering = ['name']
        verbose_name_plural = 'employment types'

    def __str__(self):
        return self.name


# ── Companies ──────────────────────────────────────────────────────────────

class Company(models.Model):
    """A company that can be searched and browsed on the Home screen.
    Table: home_company."""

    industry = models.ForeignKey(
        Industry, on_delete=models.PROTECT, related_name='companies',
    )
    name = models.CharField(max_length=150)
    location = models.CharField(max_length=100)

    # Stored aggregates, recalculated from Review rows.
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    review_count = models.PositiveIntegerField(default=0)

    # A company can offer several employment types (join table below).
    employment_types = models.ManyToManyField(
        EmploymentType,
        through='CompanyEmploymentType',
        related_name='companies',
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'home_company'
        ordering = ['-rating', '-review_count']
        verbose_name_plural = 'companies'

    def __str__(self):
        return self.name

    def employment_types_list(self):
        return [et.name for et in self.employment_types.all()]

    def update_rating_and_count(self):
        reviews = self.reviews.all()
        count = reviews.count()
        self.review_count = count
        if count > 0:
            avg = reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0
            self.rating = round(avg, 1)
        else:
            self.rating = 0
        self.save(update_fields=['rating', 'review_count'])

    def rating_distribution(self):
        """Returns the distribution and percentage of 1 to 5 star ratings."""
        counts = {i: 0 for i in range(1, 6)}
        reviews = self.reviews.all()
        total = reviews.count()
        for r in reviews:
            if 1 <= r.rating <= 5:
                counts[r.rating] += 1
        return [
            {
                'star': i,
                'count': counts[i],
                'pct': round((counts[i] / total) * 100) if total > 0 else 0,
            }
            for i in range(5, 0, -1)
        ]

    def recommendation_percentage(self):
        """Calculates percentage of ratings that are 4 or 5 stars."""
        total = self.reviews.count()
        if total == 0:
            return 0
        positive = self.reviews.filter(rating__gte=4).count()
        return round((positive / total) * 100)

    def salary_summary(self):
        """Calculates min, max, average and Philippine 13th-month annual estimate."""
        from django.db.models import Min, Max, Avg
        agg = self.salary_entries.aggregate(
            min_salary=Min('monthly_salary'),
            max_salary=Max('monthly_salary'),
            avg_salary=Avg('monthly_salary'),
        )
        avg = agg['avg_salary'] or 0
        return {
            'min': agg['min_salary'],
            'max': agg['max_salary'],
            'avg': avg,
            'annual_13th_month': avg * 13,
            'count': self.salary_entries.count(),
        }


class CompanyEmploymentType(models.Model):
    """Join table between Company and EmploymentType (many-to-many)."""

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='company_employment_types',
    )
    employment_type = models.ForeignKey(
        EmploymentType, on_delete=models.CASCADE, related_name='company_employment_types',
    )

    class Meta:
        db_table = 'company_employment_type'
        constraints = [
            models.UniqueConstraint(
                fields=['company', 'employment_type'],
                name='uniq_company_employment_type',
            ),
        ]

    def __str__(self):
        return f'{self.company} - {self.employment_type}'


# ── Reviews & salaries ─────────────────────────────────────────────────────

class Review(models.Model):
    """One user's review of one company. A user can write many reviews
    (user.reviews), and a company receives many (company.reviews).
    Table: home_review."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews',
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='reviews',
    )
    employment_type = models.ForeignKey(
        EmploymentType, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reviews',
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='1 to 5',
    )
    job_title = models.CharField(max_length=150, help_text='Role the reviewer held')
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'home_review'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} on {self.company} ({self.rating}/5)'

    def helpful_count(self):
        return self.votes.filter(is_helpful=True).count()

    def unhelpful_count(self):
        return self.votes.filter(is_helpful=False).count()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.company.update_rating_and_count()

    def delete(self, *args, **kwargs):
        company = self.company
        res = super().delete(*args, **kwargs)
        company.update_rating_and_count()
        return res


class SalaryEntry(models.Model):
    """One reported salary for a role at a company. Grouping these by
    job_title is what powers per-role average/median salary."""

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='salary_entries',
    )
    # Nullable so a submission can be anonymous.
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='salary_entries',
    )
    employment_type = models.ForeignKey(
        EmploymentType, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='salary_entries',
    )
    job_title = models.CharField(max_length=150)
    monthly_salary = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'salary_entry'
        verbose_name_plural = 'salary entries'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.job_title} at {self.company}: {self.monthly_salary}'


# ── Engagement: following, voting, moderation ──────────────────────────────

class CompanyFollow(models.Model):
    """A user following a company (many-to-many between User and Company)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='company_follows',
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='followers',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'company_follow'
        constraints = [
            models.UniqueConstraint(fields=['user', 'company'], name='uniq_company_follow'),
        ]

    def __str__(self):
        return f'{self.user} follows {self.company}'


class ReviewVote(models.Model):
    """A user marking a review helpful or not. One vote per user per review."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='review_votes',
    )
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='votes',
    )
    is_helpful = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'review_vote'
        constraints = [
            models.UniqueConstraint(fields=['user', 'review'], name='uniq_review_vote'),
        ]

    def __str__(self):
        return f'{self.user} -> review {self.review_id}: {self.is_helpful}'


class ModerationFlag(models.Model):
    """A user reporting a review for moderator attention."""

    STATUS_PENDING = 'pending'
    STATUS_REVIEWED = 'reviewed'
    STATUS_DISMISSED = 'dismissed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_REVIEWED, 'Reviewed'),
        (STATUS_DISMISSED, 'Dismissed'),
    ]

    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='flags',
    )
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='review_flags',
    )
    reason = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'moderation_flag'
        ordering = ['-created_at']

    def __str__(self):
        return f'Flag on review {self.review_id} ({self.status})'
