from django.urls import path

from . import views

app_name = 'home'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('companies/<int:pk>/', views.company_detail_view, name='company_detail'),
    path('companies/<int:pk>/follow/', views.toggle_follow_view, name='toggle_follow'),
    path('companies/<int:pk>/review/', views.add_review_view, name='add_review'),
    path('companies/<int:pk>/salary/', views.add_salary_view, name='add_salary'),
    path('reviews/<int:pk>/vote/', views.vote_review_view, name='vote_review'),
    path('reviews/<int:pk>/flag/', views.flag_review_view, name='flag_review'),
]
