from django.contrib import admin
from .models import (
    Industry, EmploymentType, Company, Review,
    SalaryEntry, CompanyFollow, ReviewVote, ModerationFlag,
)


@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    list_display  = ('name',)
    search_fields = ('name',)


@admin.register(EmploymentType)
class EmploymentTypeAdmin(admin.ModelAdmin):
    list_display  = ('name',)
    search_fields = ('name',)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display   = ('name', 'industry', 'location', 'rating', 'review_count', 'created_at')
    list_filter    = ('industry',)
    search_fields  = ('name', 'location')
    ordering       = ('-created_at',)
    readonly_fields = ('rating', 'review_count', 'created_at')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display   = ('company', 'user', 'job_title', 'rating', 'created_at')
    list_filter    = ('rating',)
    search_fields  = ('company__name', 'user__username', 'job_title', 'comment')
    ordering       = ('-created_at',)
    readonly_fields = ('created_at',)


@admin.register(SalaryEntry)
class SalaryEntryAdmin(admin.ModelAdmin):
    list_display   = ('company', 'submitted_by', 'job_title', 'monthly_salary', 'employment_type', 'created_at')
    list_filter    = ('employment_type',)
    search_fields  = ('company__name', 'submitted_by__username', 'job_title')
    ordering       = ('-created_at',)


@admin.register(CompanyFollow)
class CompanyFollowAdmin(admin.ModelAdmin):
    list_display   = ('user', 'company', 'created_at')
    search_fields  = ('user__username', 'company__name')
    ordering       = ('-created_at',)


@admin.register(ReviewVote)
class ReviewVoteAdmin(admin.ModelAdmin):
    list_display   = ('user', 'review', 'is_helpful', 'created_at')
    list_filter    = ('is_helpful',)
    search_fields  = ('user__username', 'review__company__name')


@admin.register(ModerationFlag)
class ModerationFlagAdmin(admin.ModelAdmin):
    list_display   = ('reported_by', 'review', 'reason', 'status', 'created_at')
    list_filter    = ('status',)
    search_fields  = ('reported_by__username', 'review__company__name', 'reason')
    ordering       = ('-created_at',)
