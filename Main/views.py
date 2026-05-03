from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from django.views import View
from django.db.models import Prefetch
from .models import Chat, Message


class MainView(LoginRequiredMixin, View):
    login_url = "HomePage"

    def get(self, request):
        search = request.GET.get("search_text", "").strip()
        chats = (Chat.objects.filter(participants=request.user).prefetch_related(Prefetch("messages", queryset=Message.objects.order_by("created_at"))))

        if search:
            chats = chats.filter(title__icontains=search)
        
        chats = chats.distinct()
        context = {
            "chats": chats,
            "search": search
        }

        return render(request, "Main/Main.html", context)
    
    def post(self, request):
        logout(request)
        return redirect("HomePage")
    

class ChatDetailView(LoginRequiredMixin, View):
    login_url = "HomePage"

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
    
    def post(self, request, chat_id):
        text = request.POST.get("message_text")

        active_chat = get_object_or_404(
            Chat,
            id=chat_id,
            participants=request.user
        )

        if text:
            Message.objects.create(
                chat=active_chat,
                sender=request.user,
                text=text
            )

        return redirect("ChatDetail", chat_id=chat_id)