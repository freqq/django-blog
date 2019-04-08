from django.shortcuts import render
from .forms import UserLoginForm
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout
)

# Create your views here.

def login_view(request):
    print(request.user.is_authenticated)
    form = UserLoginForm(request.POST or None)
    title = "Login"
    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(username=username, password=password)
        login(request, user)

    context = {
        "title": title,
        "form": form
    }

    return render(request, "form.html", context)

def register_view(request):
    return render(request, "form.html", {})

def logout_view(request):
    logout(request)
    return render(request, "form.html", {})