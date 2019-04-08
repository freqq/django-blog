from django.shortcuts import render, redirect
from .forms import UserLoginForm, UserRegistrationForm
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout
)

def login_view(request):
    print(request.user.is_authenticated)

    next = request.GET.get('next')
    form = UserLoginForm(request.POST or None)
    title = "Login"
    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(username=username, password=password)
        login(request, user)
        if next:
            return redirect(next)
        return redirect("/")

    context = {
        "title": title,
        "form": form
    }
    if request.user.is_authenticated:
        return HttpResponseRedirect("/")
    else:
        return render(request, "form.html", context)

def register_view(request):
    next = request.GET.get('next')
    form = UserRegistrationForm(request.POST or None)
    title = "Register"
    if form.is_valid():
        user = form.save(commit=False)
        password = form.cleaned_data.get('password')
        user.set_password(password)
        user.save()
        new_user = authenticate(username=user.username, password=password)
        login(request, new_user)
        if next:
            return redirect(next)
        return redirect("/")

    context = {
        "form": form,
        "title": title
    }
    if request.user.is_authenticated:
        return HttpResponseRedirect("/")
    else:
        return render(request, "form.html", context)

def logout_view(request):
    logout(request)
    return redirect("/")
