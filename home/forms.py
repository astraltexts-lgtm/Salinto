from django import forms
from .models import Review, SalaryEntry, ModerationFlag, EmploymentType


class ReviewForm(forms.ModelForm):
    """Form for writing a company review."""

    class Meta:
        model = Review
        fields = ['rating', 'job_title', 'employment_type', 'comment']
        widgets = {
            'rating': forms.Select(
                choices=[(i, f"{i} Star{'s' if i > 1 else ''}") for i in range(5, 0, -1)],
                attrs={'class': 'sal-input sal-select'}
            ),
            'job_title': forms.TextInput(attrs={
                'class': 'sal-input',
                'placeholder': 'e.g. Customer Support Specialist, Software Engineer',
                'required': True,
            }),
            'employment_type': forms.Select(attrs={
                'class': 'sal-input sal-select',
            }),
            'comment': forms.Textarea(attrs={
                'class': 'sal-input sal-textarea',
                'rows': 4,
                'placeholder': 'Share details on culture, compensation, management, and work-life balance...',
                'required': True,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employment_type'].empty_label = 'Select employment type (optional)'
        self.fields['employment_type'].required = False


class SalaryEntryForm(forms.ModelForm):
    """Form for reporting salary."""

    is_anonymous = forms.BooleanField(
        required=False,
        initial=False,
        label='Submit anonymously (your name will not be shown)',
        widget=forms.CheckboxInput(attrs={'class': 'sal-checkbox'})
    )

    class Meta:
        model = SalaryEntry
        fields = ['job_title', 'monthly_salary', 'employment_type']
        widgets = {
            'job_title': forms.TextInput(attrs={
                'class': 'sal-input',
                'placeholder': 'e.g. Senior Software Engineer',
                'required': True,
            }),
            'monthly_salary': forms.NumberInput(attrs={
                'class': 'sal-input',
                'placeholder': 'e.g. 45000',
                'step': '500',
                'min': '1000',
                'required': True,
            }),
            'employment_type': forms.Select(attrs={
                'class': 'sal-input sal-select',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employment_type'].empty_label = 'Select employment type (optional)'
        self.fields['employment_type'].required = False


class ModerationFlagForm(forms.ModelForm):
    """Form for reporting an inappropriate review."""

    class Meta:
        model = ModerationFlag
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(attrs={
                'class': 'sal-input sal-textarea',
                'rows': 3,
                'placeholder': 'Please specify why this review violates community standards...',
                'required': True,
            }),
        }
