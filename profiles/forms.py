from django import forms
from .models import Profile


class ProfileEditForm(forms.ModelForm):
    """Form to update public profile details."""

    class Meta:
        model = Profile
        fields = ['display_name', 'location', 'bio']
        widgets = {
            'display_name': forms.TextInput(attrs={
                'class': 'sal-input',
                'placeholder': 'Your public name (e.g. Daniel Duarte)',
            }),
            'location': forms.TextInput(attrs={
                'class': 'sal-input',
                'placeholder': 'e.g. Taguig City, Metro Manila',
            }),
            'bio': forms.Textarea(attrs={
                'class': 'sal-input sal-textarea',
                'rows': 3,
                'placeholder': 'Brief summary of your professional background or career interests...',
            }),
        }
