from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .models import User


class SignUpView(View):

    def get(self, request):
        return render(request, "Users/SignUp.html")
    
    def post(self, request):
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if password != password2:
            messages.error(request, "Password do not match")
            return redirect("SignUp")
        
        elif User.objects.filter(email=email).exists():
            messages.error(request, "User with this email already exists")
            return redirect("SignUp")
        
        else:
            user = User.objects.create(
                username=username,
                email=email,
                password=password,
            )
            login(request, user)

            return redirect("/")
        

class SignInView(View):

    def get(self, request):
        return render(request, "Users/SignIn.html")
    
    def post(self, request):
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect("/")
        
        else:
            messages.error(request, "Invalid email or password")
            return redirect("SignIn")