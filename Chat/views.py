from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from Main.models import Chat


class EditChatView(View):

    def get(self, request, chat_id):
        chat = get_object_or_404(Chat, id=chat_id)

        context = {
            "chat": chat
        }

        return render(request, "Chat/EditChat.html", context)