from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from home.models import CompanyFollow, Review, SalaryEntry
from .forms import ProfileEditForm
from .models import Profile


@login_required(login_url='login:login')
def profile_view(request):
    """
    Profile screen: displays the logged-in user's profile, followed companies,
    submitted reviews, and reported salaries.
    """
    profile, _ = Profile.objects.get_or_create(user=request.user)

    # Followed companies
    followed_companies = [
        f.company for f in CompanyFollow.objects.filter(user=request.user).select_related('company__industry')
    ]

    # User's reviews
    user_reviews = (
        Review.objects.filter(user=request.user)
        .select_related('company', 'employment_type')
        .order_by('-created_at')
    )

    # User's submitted salaries
    user_salaries = (
        SalaryEntry.objects.filter(submitted_by=request.user)
        .select_related('company', 'employment_type')
        .order_by('-created_at')
    )

    form = ProfileEditForm(instance=profile)

    context = {
        'profile': profile,
        'form': form,
        'followed_companies': followed_companies,
        'user_reviews': user_reviews,
        'user_salaries': user_salaries,
    }
    return render(request, 'profiles/profile.html', context)


@login_required(login_url='login:login')
@require_POST
def edit_profile_view(request):
    """Handles updating the user profile."""
    profile, _ = Profile.objects.get_or_create(user=request.user)
    form = ProfileEditForm(request.POST, instance=profile)
    if form.is_valid():
        form.save()
        messages.success(request, 'Your profile has been updated successfully!')
    else:
        messages.error(request, 'Failed to update profile. Please check the input fields.')

    return redirect('profiles:profile')


@login_required(login_url='login:login')
@require_POST
def delete_my_review_view(request, pk):
    """Allows a user to remove their own review."""
    review = get_object_or_404(Review, pk=pk, user=request.user)
    company_name = review.company.name
    review.delete()
    messages.info(request, f'Your review for {company_name} was removed.')
    return redirect('profiles:profile')
