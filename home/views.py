from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ModerationFlagForm, ReviewForm, SalaryEntryForm
from .models import (
    Company,
    CompanyFollow,
    EmploymentType,
    Industry,
    ModerationFlag,
    Review,
    ReviewVote,
    SalaryEntry,
)


@login_required(login_url='login:login')
def home_view(request):
    """
    Home Screen slice: Philippine workplace transparency directory.
    Queries Supabase PostgreSQL for companies with search and industry filtering.
    """
    query = request.GET.get('q', '').strip()
    selected_industry = request.GET.get('industry', '').strip()
    min_rating = request.GET.get('min_rating', '').strip()

    companies = Company.objects.select_related('industry').prefetch_related('employment_types').all()

    if query:
        companies = companies.filter(
            models.Q(name__icontains=query) |
            models.Q(location__icontains=query) |
            models.Q(industry__name__icontains=query)
        )

    if selected_industry:
        companies = companies.filter(industry__name__iexact=selected_industry)

    if min_rating:
        try:
            val = float(min_rating)
            companies = companies.filter(rating__gte=val)
        except ValueError:
            pass

    industries = Industry.objects.annotate(comp_count=Count('companies')).filter(comp_count__gt=0)
    
    # Platform statistics
    total_companies = Company.objects.count()
    total_reviews = Review.objects.count()
    total_salaries = SalaryEntry.objects.count()

    # User's followed company IDs for badge status
    followed_ids = set(
        CompanyFollow.objects.filter(user=request.user).values_list('company_id', flat=True)
    )

    context = {
        'companies': companies,
        'query': query,
        'selected_industry': selected_industry,
        'min_rating': min_rating,
        'industries': industries,
        'total_companies': total_companies,
        'total_reviews': total_reviews,
        'total_salaries': total_salaries,
        'followed_ids': followed_ids,
    }
    return render(request, 'home/home.html', context)


@login_required(login_url='login:login')
def company_detail_view(request, pk):
    """
    Company Detail screen: displays full company profile, reviews,
    salary entries, and submission forms.
    """
    company = get_object_or_404(
        Company.objects.select_related('industry').prefetch_related('employment_types'),
        pk=pk
    )

    is_following = CompanyFollow.objects.filter(user=request.user, company=company).exists()
    followers_count = company.followers.count()

    # Reviews with user votes
    reviews = company.reviews.select_related('user', 'user__profile', 'employment_type').all()
    user_votes = {
        v.review_id: v.is_helpful
        for v in ReviewVote.objects.filter(user=request.user, review__in=reviews)
    }

    # Salaries grouped by role
    salaries = company.salary_entries.select_related('employment_type', 'submitted_by').all()
    roles_summary = (
        company.salary_entries
        .values('job_title')
        .annotate(avg_salary=Avg('monthly_salary'), count=Count('id'))
        .order_by('-avg_salary')
    )

    overall_avg_salary = company.salary_entries.aggregate(avg=Avg('monthly_salary'))['avg']

    active_tab = request.GET.get('tab', 'reviews')

    review_form = ReviewForm()
    salary_form = SalaryEntryForm()
    flag_form = ModerationFlagForm()

    context = {
        'company': company,
        'is_following': is_following,
        'followers_count': followers_count,
        'reviews': reviews,
        'user_votes': user_votes,
        'salaries': salaries,
        'roles_summary': roles_summary,
        'overall_avg_salary': overall_avg_salary,
        'active_tab': active_tab,
        'review_form': review_form,
        'salary_form': salary_form,
        'flag_form': flag_form,
    }
    return render(request, 'home/company_detail.html', context)


@login_required(login_url='login:login')
@require_POST
def toggle_follow_view(request, pk):
    """Toggles following status for the given company."""
    company = get_object_or_404(Company, pk=pk)
    follow_obj = CompanyFollow.objects.filter(user=request.user, company=company).first()
    if follow_obj:
        follow_obj.delete()
        messages.info(request, f'You unfollowed {company.name}.')
    else:
        CompanyFollow.objects.create(user=request.user, company=company)
        messages.success(request, f'You are now following {company.name}!')

    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')
    return redirect(next_url or 'home:company_detail', pk=pk)


@login_required(login_url='login:login')
@require_POST
def add_review_view(request, pk):
    """Submits a new review for the company."""
    company = get_object_or_404(Company, pk=pk)
    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.user = request.user
        review.company = company
        review.save()
        messages.success(request, 'Thank you! Your workplace review has been published.')
    else:
        messages.error(request, 'Could not post review. Please check the fields and try again.')

    return redirect(f"{redirect('home:company_detail', pk=pk).url}?tab=reviews")


@login_required(login_url='login:login')
@require_POST
def add_salary_view(request, pk):
    """Submits a new salary report for a role at the company."""
    company = get_object_or_404(Company, pk=pk)
    form = SalaryEntryForm(request.POST)
    if form.is_valid():
        salary = form.save(commit=False)
        salary.company = company
        if not form.cleaned_data.get('is_anonymous'):
            salary.submitted_by = request.user
        else:
            salary.submitted_by = None
        salary.save()
        messages.success(request, 'Salary insight recorded! Thank you for promoting workplace transparency.')
    else:
        messages.error(request, 'Could not submit salary. Please ensure salary amount is valid.')

    return redirect(f"{redirect('home:company_detail', pk=pk).url}?tab=salaries")


@login_required(login_url='login:login')
@require_POST
def vote_review_view(request, pk):
    """Records whether a user found a review helpful or not."""
    review = get_object_or_404(Review, pk=pk)
    is_helpful = request.POST.get('is_helpful', 'true').lower() in ('true', '1')

    vote = ReviewVote.objects.filter(user=request.user, review=review).first()
    if vote:
        if vote.is_helpful == is_helpful:
            vote.delete()  # toggle off
        else:
            vote.is_helpful = is_helpful
            vote.save()
    else:
        ReviewVote.objects.create(user=request.user, review=review, is_helpful=is_helpful)

    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')
    return redirect(next_url or 'home:company_detail', pk=review.company_id)


@login_required(login_url='login:login')
@require_POST
def flag_review_view(request, pk):
    """Flags a review for community moderation."""
    review = get_object_or_404(Review, pk=pk)
    form = ModerationFlagForm(request.POST)
    if form.is_valid():
        flag = form.save(commit=False)
        flag.review = review
        flag.reported_by = request.user
        flag.status = ModerationFlag.STATUS_PENDING
        flag.save()
        messages.info(request, 'Review flagged for moderator review. Thank you for keeping Salinto safe.')
    else:
        messages.error(request, 'Could not submit report. Please specify a reason.')

    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')
    return redirect(next_url or 'home:company_detail', pk=review.company_id)
