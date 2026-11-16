from django.urls import path

from . import views

app_name = 'profiles'

urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('profile/reviews/<int:pk>/delete/', views.delete_my_review_view, name='delete_review'),
]
