from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm = request.POST['confirm']

        if password != confirm:
            
            return redirect('register')

        if User.objects.filter(username=username).exists():
           
            return redirect('register')

        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect('home')
  # or your app's main page

    return render(request, 'accounts/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')  # or your app's main page
        else:
            
            return redirect('login')

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')
