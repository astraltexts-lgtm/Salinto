from django import forms


class LoginForm(forms.Form):
    """Plain login form; authentication itself is handled in the view."""

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'sal-input',
            'placeholder': 'Username',
            'autocomplete': 'username',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'sal-input',
            'placeholder': 'Password',
            'autocomplete': 'current-password',
        })
    )
