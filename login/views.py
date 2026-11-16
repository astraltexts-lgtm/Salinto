from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import LoginForm


def login_view(request):
    """Handles the Login screen: authenticate an existing user."""
    if request.user.is_authenticated:
        return redirect('home:home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                return redirect('home:home')
            form.add_error(None, 'Incorrect username or password. Please try again.')
    else:
        form = LoginForm()

    return render(request, 'login/login.html', {'form': form})


@login_required(login_url='login:login')
def logout_view(request):
    """
    Logs the current user out.

    Logout isn't one of the three required screens, but it lives here
    since ending a session is the natural counterpart to starting one.
    """
    logout(request)
    messages.success(request, 'You have been logged out safely.')
    return redirect('login:login')
