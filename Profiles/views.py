from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.conf import settings
from Users.models import User
from .models import Profile


class ProfilesView(LoginRequiredMixin, View):
    login_url = "HomePage"

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)

        return render(request, "Profiles/Profiles.html", {"user": user})