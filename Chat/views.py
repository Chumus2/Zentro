from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from Main.models import Chat


class EditChatView(LoginRequiredMixin, View):
    login_url = "HomePage"

    def get(self, request, chat_id):
        chat = get_object_or_404(Chat, id=chat_id)

        if not chat.admins.filter(id=request.user.id).exists():
            return redirect("ChatDetail", chat_id=chat.id)
        if not chat.participants.filter(id=request.user.id).exists():
            return redirect("Main")

        return render(request, "Chat/EditChat.html", {"chat": chat})
    
    def post(self, request, chat_id):
        title = request.POST.get("chat_title")
        description = request.POST.get("chat_description", "").strip()

        chat = get_object_or_404(Chat, id=chat_id)

        if not chat.admins.filter(id=request.user.id).exists():
            return redirect("ChatDetail", chat_id=chat.id)
        if not chat.participants.filter(id=request.user.id).exists():
            return redirect("Main")

        form_data = {
            "title": title,
            "description": description
        }

        if not title:
            messages.error(request, "Title is required")
            return render(request, "Chat/EditChat.html", {"chat": chat, "form_data": form_data})
        if len(description) > 255:
            messages.error(request, "Description must be under 255 characters long")
            return render(request, "Chat/EditChat.html", {"chat": chat, "form_data": form_data})
            

        chat.title = title
        chat.description = description
        chat.save()

        return redirect("ChatDetail", chat_id=chat.id)
    

class ChatParticipantsView(LoginRequiredMixin, View):
    login_url="HomePage"

    def get(self, request, chat_id):
        search = request.GET.get("search")

        chat = get_object_or_404(Chat, id=chat_id)

        participants = chat.participants.select_related("profile").all()
        admins = set(chat.admins.values_list("id", flat=True))
        is_admin = chat.admins.filter(id=request.user.id).exists()

        if not chat.participants.filter(id=request.user.id).exists():
            return redirect("Main")
        
        if search:
            participants = participants.filter(name__icontains=search).distinct()


        context = {
            "participants": participants,
            "chat": chat,
            "admins": admins,
            "is_admin": is_admin
        }

        return render(request, "Chat/Participants.html", context)
    
    def post(self, request, chat_id):
        action = request.POST.get("admin_button")
        participant_id = request.POST.get("participant_id")

        chat = get_object_or_404(Chat, id=chat_id)
        participant = get_object_or_404(chat.participants, id=participant_id)

        if not chat.participants.filter(id=request.user.id).exists():
            return redirect("Main")
        

        if action == "add_admin":
            if request.user == chat.creator:
                chat.admins.add(participant)
                return redirect("Participants", chat_id=chat.id)
        
        elif action == "remove_admin":
            if request.user == chat.creator and participant != chat.creator:
                chat.admins.remove(participant)
                return redirect("Participants", chat_id=chat.id)
            

class AddParticipantView(LoginRequiredMixin, View):
    login_url = "HomePage"

    def get(self, request):
        pass