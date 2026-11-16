"""
URL configuration for salinto_project.

Self-contained vertical slices:
  - login/         -> Authentication (Login, Logout)
  - register/      -> Registration
  - home/          -> Company directory, search, company details, reviews, salaries, voting
  - profiles/      -> User profile, followed companies, review management
  - user_settings/ -> User notification preferences
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('login.urls')),
    path('', include('register.urls')),
    path('', include('home.urls')),
    path('', include('profiles.urls')),
    path('', include('user_settings.urls')),
]
