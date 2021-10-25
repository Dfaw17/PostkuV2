from django.shortcuts import *
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from ..forms import *
import locale

locale.setlocale(locale.LC_ALL, '')

def loginpage(requets):
    if requets.method == "POST":
        username = requets.POST.get('username')
        password = requets.POST.get('password')
        user = authenticate(requets, username=username, password=password)

        if user is not None:
            if user.is_superuser == 1:
                login(requets, user)
                return redirect('home')
            else:
                return redirect('wrong_access')
        else:
            messages.error(requets, 'Username or Password Failed')
    context = {}
    return render(requets, 'webadmin/login.html', context)


def registerpage(requets):
    form = RegisterForm()

    if requets.method == "POST":
        form = RegisterForm(requets.POST)
        if form.is_valid():
            form.save()
            messages.success(requets, 'Register successfully')
            return redirect('login')

    context = {
        'form': form,
    }
    return render(requets, 'webadmin/register.html', context)


def wrong_access(requets):
    context = {
    }
    return render(requets, 'webadmin/404.html', context)


@login_required(login_url='login')
def logoutpage(requets):
    logout(requets)
    return redirect('login')