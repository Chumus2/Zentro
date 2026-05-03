from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View


class MainView(LoginRequiredMixin, View):
    login_url = "SignIn"

    def get(self, request):
        return render(request, "Main/Main.html")