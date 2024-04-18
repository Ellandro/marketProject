from django.shortcuts import render, redirect
from .forms import CreateUserForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth import logout as auth_logout, login
from django.contrib import messages


# Create your views here.
def register(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,f'Votre compte a bien été cree {username}')
            return redirect('dashboard:dashboard')
    else:
        form = CreateUserForm()
    context = {
        'form': form
    }
    return render(request, 'users/register.html', context)


def user_logout(request):
    auth_logout(request)
    return redirect('user-login')

def profile(request):
    context={

    }
    return render(request, 'users/accounts.html', context)

def update_profile(request):
    if request.method=="POST":
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profil_form = ProfileUpdateForm(request.POST,request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profil_form.is_valid():
            user_form.save()
            profil_form.save()
            return redirect('product')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profil_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form':user_form,
        'profil_form':profil_form,
    }
    return render(request, 'users/accounts.html', context)
