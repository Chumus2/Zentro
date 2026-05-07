from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from django.contrib import messages
from django.views import View
from django.db.models import Prefetch
from Users.models import User
from .models import *


class MainView(LoginRequiredMixin, View):
    login_url = "HomePage"

    def get(self, request):
        search = request.GET.get("search_text", "").strip()
        chats = (Chat.objects.filter(participants=request.user).prefetch_related(Prefetch("messages", queryset=Message.objects.order_by("created_at"))))

        if search:
            chats = chats.filter(title__icontains=search).distinct()

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

        is_admin = active_chat.admins.filter(id=request.user.id).exists()
        messages = active_chat.messages.all().order_by("created_at")

        context = {
            "chats": chats,
            "active_chat": active_chat,
            "messages": messages,
            "is_admin": is_admin
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
    

class ParticipantLeaveView(LoginRequiredMixin, View):
    login_url="HomePage"

    def get(self, request, chat_id):
        chat = get_object_or_404(Chat, id=chat_id)

        if not chat.participants.filter(id=request.user.id).exists():
            return redirect("Main")
        
        return render(request, "Main/Main.html", {"chat": chat}) 
    
    def post(self, request, chat_id):
        user = request.user
        chat = get_object_or_404(Chat, id=chat_id)

        if not chat.participants.filter(id=user.id).exists():
            return redirect("Main")
        
        chat.participants.remove(user)
        chat.admins.remove(user)
        chat.delete_if_empty()
        chat.save()

        Message.objects.create(
            chat=chat,
            sender=None,
            text=f"User {user.name} leaved from this group",
            if_system=True
        )

        return redirect("Main")
    

class CreateChatView(LoginRequiredMixin, View):
    login_url = "HomePage"

    def get(self, request):
        friends = request.user.profile.friends.all()

        return render(request, "Chat/ChatCreation.html", {"friends": friends})
    
    def post(self, request):
        user = request.user
        title = request.POST.get("chat_title", "").strip()
        description = request.POST.get("chat_description", "").strip()
        chat_icon = request.FILES.get("chat_icon")
        selected_friends = request.POST.getlist("friend_choose")

        form_data = {
            "title": title,
            "description": description
        }

        if not title:
            messages.error(request, "Title is required")
            return render(request, "Chat/ChatCreation.html", {"form_data": form_data})

        if len(description) > 255:
            messages.error(request, "Description must be under 255 characters long")
            return render(request, "Chat/ChatCreation.html", {"form_data": form_data})

        if chat_icon and chat_icon.content_type not in {"image/png", "image/jpeg"}:
            messages.error(request, "Only PNG and JPG images are allowed")
            return render(request, "Chat/ChatCreation.html", {"form_data": form_data})

        chat = Chat.objects.create(
            title=title,
            description=description,
            icon=chat_icon,
            creator=user
        )
        chat.participants.add(user)
        chat.admins.add(user)

        if selected_friends:
            friends = User.objects.filter(
                profile__in=user.profile.friends.filter(user__id__in=selected_friends)
            )
            chat.participants.add(*friends)

        Message.objects.create(
            chat=chat,
            sender=None,
            text=f"Chat {title} successfuly created!",
            if_system=True
        )

        return redirect("ChatDetail", chat_id=chat.id)