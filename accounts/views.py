from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from .forms import CustomerUserCreationForm, ProfileUpdateForm

# Create your views here.


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'


def register(request):
    if request.method == 'POST':
        form = CustomerUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)

            return redirect('home')
    else:
        form = CustomerUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required()
def profile(request):
    user_profile = request.user.profile
    context = {
        'user_profile': user_profile
    }

    return render(request, 'accounts/profile.html', context)


@login_required
def profile_update(request):
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=user, profile_instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ваш профиль успешно обновлен!')
            return redirect('profile')

    else:
        form = ProfileUpdateForm(instance=user, profile_instance=profile)

    context = {
        'form': form,
        'user_profile': profile
    }

    return render(request, 'accounts/profile_update.html', context)