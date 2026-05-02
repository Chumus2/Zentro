import re
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User


class SignUpView(View):

    def get(self, request):
        return render(request, "Users/SignUp.html")
    
    def post(self, request):
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")


        # General checks
        if not name or not email or not password or not password2:
            messages.error(request, "All fields are required")
            return redirect("SignUp")
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "User with this email already exists")
            return redirect("SignUp")
        
        if not re.search(r"\d", name):
            messages.error(request, "Name must contain at least 1 digit.")
            return redirect("SignUp")


        # Name checks
        if len(name) < 4:
            messages.error(request, "Name must be at least 4 characters long")
            return redirect("SignUp")
        
        # Email checks
        if password != password2:
            messages.error(request, "Password do not match")
            return redirect("SignUp")
        
        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long")
            return redirect("SignUp")
        
        if not re.search(r"[^\w\s]", password):
            messages.error(request, "Password must contain at least 1 special character")
            return redirect("SignUp")

        if len(re.findall(r"\d", password)) < 3:
            messages.error(request, "Password must contain at least 3 digits")
            return redirect("SignUp")

        temp_user = User(email=email)
        try:
            validate_password(password, user=temp_user)
        except ValidationError as error:
            for message in error.messages:
                messages.error(request, message)
            return redirect("SignUp")
        

        user = User.objects.create_user(
            name=name,
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