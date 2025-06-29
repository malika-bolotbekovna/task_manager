# users/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Profile
from .forms import UserRegisterForm, ProfileForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login


def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            # Создаем профиль
            Profile.objects.create(user=user, avatar=form.cleaned_data.get('avatar'))
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile_view(request):
    return render(request, 'users/profile.html')

@login_required
def profile_edit(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'users/profile_edit.html', {'form': form})