from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import RegisterForm


def register_view(request):
    """Handles the Register screen: create a new Salinto account."""
    if request.user.is_authenticated:
        return redirect('home:home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to Salinto, {user.username}!')
            return redirect('home:home')
    else:
        form = RegisterForm()

    return render(request, 'register/register.html', {'form': form})
