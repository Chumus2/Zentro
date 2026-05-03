from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from .models import Chat


class MainView(LoginRequiredMixin, View):
    login_url = "SignIn"

    def get(self, request):
        chats = Chat.objects.filter(participants=request.user).distinct()

        context = {
            "chats": chats
        }

        return render(request, "Main/Main.html", context)
    

class ChatDetailView(LoginRequiredMixin, View):
    login_url = "SignIn"

    def get(self, request, chat_id):
        chats = Chat.objects.filter(participants=request.user).distinct()
        active_chat = get_object_or_404(
            Chat.objects.prefetch_related("messages"),
            id=chat_id,
            participants=request.user
        )

        messages = active_chat.messages.all().order_by("created_at")

        context = {
            "chats": chats,
            "active_chat": active_chat,
            "messages": messages
        }

        return render(request, "Main/Main.html", context)