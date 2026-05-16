from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from django.contrib import messages
from django.views import View
from django.db.models import Count, Prefetch
from Users.models import User
from .models import *


def get_chats_with_user_messages(user):
    return Chat.objects.filter(participants=user).prefetch_related(
        Prefetch(
            "messages",
            queryset=(
                Message.objects
                .filter(if_system=False)
                .select_related("poll")
                .prefetch_related(
                    Prefetch(
                        "attachments",
                        queryset=MessageAttachment.objects.order_by("id"),
                        to_attr="prefetched_attachments",
                    )
                )
                .order_by("created_at")
            ),
            to_attr="user_messages"
    ))


class MainView(LoginRequiredMixin, View):
    login_url = "HomePage"

    def get(self, request):
        search = request.GET.get("search_text", "").strip()
        chats = get_chats_with_user_messages(request.user)

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
        chats = get_chats_with_user_messages(request.user).distinct()
        active_chat = get_object_or_404(
            Chat.objects.annotate(participant_count=Count("participants", distinct=True)),
            id=chat_id,
            participants=request.user
        )

        is_admin = active_chat.admins.filter(id=request.user.id).exists()
        chat_messages = active_chat.messages.select_related(
            "sender",
            "sender__profile",
            "reply_to",
            "reply_to__sender",
            "reply_to__sender__profile",
            "poll",
        ).prefetch_related(
            Prefetch(
                "attachments",
                queryset=MessageAttachment.objects.order_by("id"),
                to_attr="prefetched_attachments"
            ),
            Prefetch(
                "poll__options",
                queryset=PollOption.objects.order_by("id")
            ),
            Prefetch(
                "poll__options__votes",
                queryset=PollVote.objects.filter(user=request.user),
                to_attr="user_votes"
            )
        ).order_by("created_at")

        pinned_messages = active_chat.pinned_messages.select_related(
            "sender",
            "sender__profile",
            "poll",
        ).prefetch_related(
            Prefetch(
                "attachments",
                queryset=MessageAttachment.objects.order_by("id"),
                to_attr="prefetched_attachments"
            )
        ).order_by("-created_at")
        pinned_message_ids = set(pinned_messages.values_list("id", flat=True))

        for pinned_message in pinned_messages:
            poll = getattr(pinned_message, "poll", None)
            attachment = pinned_message.prefetched_attachments[0] if pinned_message.prefetched_attachments else None

            pinned_message.pinned_text = (
                pinned_message.text
                or (poll.title if poll else "")
                or (attachment.file.name.split("/")[-1] if attachment else "")
            )

        for message in chat_messages:
            if hasattr(message, "poll"):
                options = list(message.poll.options.all())
                total_votes = message.poll.votes.count()
                max_percent = 0

                for option in options:
                    option_votes = option.votes.count()
                    option.percent = (option_votes / total_votes) * 100 if total_votes > 0 else 0

                    if option.percent > max_percent:
                        max_percent = option.percent

                leaders_count = sum(1 for option in options if option.percent == max_percent and max_percent > 0)

                for option in options:
                    option.is_leading = leaders_count == 1 and option.percent == max_percent

                message.poll_options = options

        context = {
            "chats": chats,
            "active_chat": active_chat,
            "chat_messages": chat_messages,
            "is_admin": is_admin,
            "participant_count": active_chat.participant_count,
            "pinned_messages": pinned_messages,
            "pinned_message_ids": pinned_message_ids,
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
