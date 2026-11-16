from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Avg, Count
from django.http import JsonResponse
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
    Queries Supabase PostgreSQL for companies with search, industry filtering, and sorting.
    """
    query = request.GET.get('q', '').strip()
    selected_industry = request.GET.get('industry', '').strip()
    min_rating = request.GET.get('min_rating', '').strip()
    sort_by = request.GET.get('sort', '-rating').strip()

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

    # Sort options
    sort_mapping = {
        'highest': '-rating',
        'reviews': '-review_count',
        'name': 'name',
        'newest': '-created_at',
    }
    companies = companies.order_by(sort_mapping.get(sort_by, '-rating'), '-review_count')

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
        'sort_by': sort_by,
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
    Company Detail screen: displays full company profile, ratings distribution,
    reviews, salary benchmarks, 13th-month estimates, and submission forms.
    """
    company = get_object_or_404(
        Company.objects.select_related('industry').prefetch_related('employment_types'),
        pk=pk
    )

    is_following = CompanyFollow.objects.filter(user=request.user, company=company).exists()
    followers_count = company.followers.count()

    # Rating distribution breakdown & recommendation rate
    rating_distribution = company.rating_distribution()
    recommendation_pct = company.recommendation_percentage()
    salary_summary = company.salary_summary()

    # Reviews with user votes and sorting
    reviews_qs = company.reviews.select_related('user', 'user__profile', 'employment_type').all()
    
    review_sort = request.GET.get('review_sort', 'newest')
    rating_filter = request.GET.get('star', '')

    if rating_filter and rating_filter.isdigit():
        reviews_qs = reviews_qs.filter(rating=int(rating_filter))

    if review_sort == 'highest':
        reviews_qs = reviews_qs.order_by('-rating', '-created_at')
    elif review_sort == 'lowest':
        reviews_qs = reviews_qs.order_by('rating', '-created_at')
    else:  # newest
        reviews_qs = reviews_qs.order_by('-created_at')

    reviews = list(reviews_qs)
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

    active_tab = request.GET.get('tab', 'reviews')

    review_form = ReviewForm()
    salary_form = SalaryEntryForm()
    flag_form = ModerationFlagForm()

    context = {
        'company': company,
        'is_following': is_following,
        'followers_count': followers_count,
        'rating_distribution': rating_distribution,
        'recommendation_pct': recommendation_pct,
        'salary_summary': salary_summary,
        'reviews': reviews,
        'user_votes': user_votes,
        'review_sort': review_sort,
        'rating_filter': rating_filter,
        'salaries': salaries,
        'roles_summary': roles_summary,
        'active_tab': active_tab,
        'review_form': review_form,
        'salary_form': salary_form,
        'flag_form': flag_form,
    }
    return render(request, 'home/company_detail.html', context)


@login_required(login_url='login:login')
def compare_companies_view(request):
    """
    Workplace Comparison Tool:
    Allows Philippine job seekers to evaluate two companies side-by-side
    on compensation, ratings, review volume, and employment terms.
    """
    company_id_1 = request.GET.get('c1')
    company_id_2 = request.GET.get('c2')

    all_companies = Company.objects.all().order_by('name')

    company1 = Company.objects.filter(pk=company_id_1).first() if company_id_1 else None
    company2 = Company.objects.filter(pk=company_id_2).first() if company_id_2 else None

    # Fallback default pair if none selected
    if not company1 and all_companies.exists():
        company1 = all_companies[0]
    if not company2 and all_companies.count() > 1:
        company2 = all_companies[1]

    data1 = company1.salary_summary() if company1 else None
    data2 = company2.salary_summary() if company2 else None

    context = {
        'all_companies': all_companies,
        'company1': company1,
        'company2': company2,
        'data1': data1,
        'data2': data2,
    }
    return render(request, 'home/compare.html', context)


@login_required(login_url='login:login')
@require_POST
def toggle_follow_view(request, pk):
    """Toggles following status for the given company with AJAX & POST support."""
    company = get_object_or_404(Company, pk=pk)
    follow_obj = CompanyFollow.objects.filter(user=request.user, company=company).first()
    
    if follow_obj:
        follow_obj.delete()
        is_following = False
        msg = f'You unfollowed {company.name}.'
    else:
        CompanyFollow.objects.create(user=request.user, company=company)
        is_following = True
        msg = f'You are now following {company.name}!'

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'ok',
            'is_following': is_following,
            'followers_count': company.followers.count(),
            'message': msg,
        })

    if is_following:
        messages.success(request, msg)
    else:
        messages.info(request, msg)

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
        messages.success(request, 'Salamat! Your workplace review has been published.')
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
    """Records helpful/unhelpful votes with AJAX & standard POST support."""
    review = get_object_or_404(Review, pk=pk)
    is_helpful = request.POST.get('is_helpful', 'true').lower() in ('true', '1')

    vote = ReviewVote.objects.filter(user=request.user, review=review).first()
    user_state = None
    if vote:
        if vote.is_helpful == is_helpful:
            vote.delete()  # toggle off
            user_state = None
        else:
            vote.is_helpful = is_helpful
            vote.save()
            user_state = is_helpful
    else:
        ReviewVote.objects.create(user=request.user, review=review, is_helpful=is_helpful)
        user_state = is_helpful

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'ok',
            'helpful_count': review.helpful_count(),
            'unhelpful_count': review.unhelpful_count(),
            'user_vote': user_state,
        })

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
        messages.info(request, 'Review submitted to moderation queue. Thank you for keeping Salinto authentic.')
    else:
        messages.error(request, 'Could not submit report. Please specify a reason.')

    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')
    return redirect(next_url or 'home:company_detail', pk=review.company_id)
