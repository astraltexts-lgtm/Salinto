"""
URL configuration for salinto_project.

Each Django app below is a self-contained vertical slice, one per
required screen:
  - login/    -> Login screen (and Logout, its natural counterpart)
  - register/ -> Register screen
  - home/     -> Home screen
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('login.urls')),
    path('', include('register.urls')),
    path('', include('home.urls')),
]
