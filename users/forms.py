from django import forms
from .models import Profile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

# Форма для профиля (аватар)
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']

# Форма для редактирования пользователя (имя, email и т.п.)
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username' ]