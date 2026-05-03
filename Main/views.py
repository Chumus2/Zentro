from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from .models import Chat


class MainView(LoginRequiredMixin, View):
    login_url = "SignIn"

    def get(self, request):
        chats = Chat.objects.all()

        context = {"chats": chats}

        return render(request, "Main/Main.html", context)