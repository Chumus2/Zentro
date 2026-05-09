import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django_countries import countries
from django.contrib import messages
from django.views import View
from django.conf import settings
from Users.models import User
from .models import Profile


class ProfilesView(LoginRequiredMixin, View):
    login_url = "HomePage"

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)

        context = {
            "user": user,
            "countries": countries
        }

        return render(request, "Profiles/Profiles.html", context)
    
    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        profile = user.profile

        if request.user != user:
            return redirect("Main")

        name = request.POST.get("name")
        bio = request.POST.get("bio")
        birthday = request.POST.get("birthday")
        country = request.POST.get("country")
        icon = request.FILES.get("icon")

        context = {
            "user": user,
            "countries": countries,
        }

        # Name checks
        if name:
            if len(name) < 4:
                messages.error(request, "Name must be at least 4 characters long")
                return render(request, "Profiles/Profiles.html", context)
        
            if not re.search(r"\d", name):
                messages.error(request, "Name must contain at least 1 digit.")
                return render(request, "Profiles/Profiles.html", context)
            
            user.name = name
            user.save()
        
        # Bio checks
        if bio is not None:
            if len(bio) > 200:
                messages.error(request, "Bio can't be more than 200 characters long")
                return render(request, "Profiles/Profiles.html", context)
            
            profile.bio = bio

        if birthday:
            try:
                profile.birthday = birthday
            except (ValueError, ValidationError):
                messages.error(request, "Invalid date format")
                return render(request, "Profiles/Profiles.html", context)

        if country:
            profile.country = country
        if icon:
            profile.icon = icon
        
        profile.save()

        return redirect("CheckProfile", user_id=user.id)