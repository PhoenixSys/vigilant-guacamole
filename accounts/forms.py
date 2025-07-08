from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = False  # Deactivate account until admin approval
        if commit:
            user.save()
            # UserProfile is created by a signal, so no need to handle it here directly
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('bio', 'profile_picture')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # You can add custom styling or attributes to fields here if needed
        # For example, adding a class for styling:
        self.fields['bio'].widget.attrs.update({'class': 'form-control'})
        self.fields['profile_picture'].widget.attrs.update({'class': 'form-control-file'})

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add common form-control class to all fields
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})
