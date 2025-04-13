from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class CustomUserCreationForm(UserCreationForm):
    FORBIDDEN_USERNAMES = ['admin', 'user', 'username', 'administrator']

    class Meta(UserCreationForm.Meta):
        model = User  # Explicitly tie to User model
        fields = ("username","email", "password1", "password2")

    def clean_username(self):
        username = self.cleaned_data.get('username').lower()
        
        # Check against forbidden usernames
        if username in self.FORBIDDEN_USERNAMES:
            raise ValidationError("This username is not allowed.")
        
        # Check if username already exists
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("Username already exists.")
        
        return username