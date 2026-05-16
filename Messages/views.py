from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Prefetch
from Main.views import get_chats_with_user_messages
from Main.models import Message, Chat, MessageAttachment, Poll, PollOption, PollVote


@login_required(login_url="HomePage")
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    chat = message.chat

    if not chat.participants.filter(id=request.user.id).exists():
        return redirect("Main")

    is_admin = chat.admins.filter(id=request.user.id).exists()

    if message.sender != request.user and not is_admin:
        return redirect("ChatDetail", chat_id=chat.id)
    
    message.delete()

    return redirect("ChatDetail", chat_id=chat.id)


@login_required(login_url="HomePage")
def pin_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    chat = message.chat

    if not chat.participants.filter(id=request.user.id).exists():
        return redirect("Main")
    if not chat.admins.filter(id=request.user.id).exists():
        return redirect("ChatDetail", chat_id=chat.id)
    
    chat.pinned_messages.add(message)

    poll = getattr(message, "poll", None)
    attachment = message.attachments.first()
    pinned_text = (
        message.text 
        or (poll.title if poll else "")
        or (attachment.file.name if attachment else "")
    )

    Message.objects.create(
        chat=chat,
        sender=None,
        text=f"Message ({pinned_text}) have been pinned",
        if_system=True
    )

    return redirect("ChatDetail", chat_id=chat.id)


@login_required(login_url="HomePage")
def unpin_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    chat = message.chat

    if not chat.participants.filter(id=request.user.id).exists():
        return redirect("Main")
    if not chat.admins.filter(id=request.user.id).exists():
        return redirect("ChatDetail", chat_id=chat.id)
    
    chat.pinned_messages.remove(message)

    poll = getattr(message, "poll", None)
    attachment = message.attachments.first()
    pinned_text = (
        message.text 
        or (poll.title if poll else "")
        or (attachment.file.name if attachment else "")
    )

    Message.objects.create(
        chat=chat,
        sender=None,
        text=f"Message ({pinned_text}) have been unpinned",
        if_system=True
    )

    return redirect("ChatDetail", chat_id=chat.id)


@login_required(login_url="HomePage")
def edit_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    chat = message.chat

    if not chat.participants.filter(id=request.user.id).exists():
        return redirect("Main")
    if not message.sender == request.user:
        return redirect("ChatDetail", chat_id=chat.id)
    
    if request.method == "POST":
        new_text = request.POST.get("message_text", "").strip()

        if new_text:
            message.text = new_text
            message.save()

    return redirect("ChatDetail", chat_id=chat.id)


@login_required(login_url="HomePage")
def reply_to_message(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)

    if not chat.participants.filter(id=request.user.id).exists():
        return redirect("Main")

    if request.method == "POST":
        text = request.POST.get("message_text", "").strip()
        reply_to_id = request.POST.get("reply_to_id")

        reply_to = None
        if reply_to_id:
            reply_to = Message.objects.filter(id=reply_to_id, chat=chat).first()
        if text:
            Message.objects.create(
                chat=chat,
                sender=request.user,
                text=text,
                reply_to=reply_to
            )

            return redirect("ChatDetail", chat_id=chat.id)

    chat_messages = chat.messages.select_related(
        "sender",
        "sender__profile",
        "reply_to",
        "reply_to__sender",
        "reply_to__sender__profile",
        "reply_to__poll",
        "poll",
    ).prefetch_related(
        Prefetch(
            "attachments",
            queryset=MessageAttachment.objects.order_by("id"),
            to_attr="prefetched_attachments"
        ),
        Prefetch(
            "reply_to__attachments",
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

        if message.reply_to:
            reply_poll = getattr(message.reply_to, "poll", None)
            reply_attachment = message.reply_to.prefetched_attachments[0] if getattr(message.reply_to, "prefetched_attachments", None) else None

            message.reply_preview_text = (
                message.reply_to.text
                or (reply_poll.title if reply_poll and reply_poll.title else "")
                or (reply_poll.question if reply_poll else "")
                or (reply_attachment.file.name.split("/")[-1] if reply_attachment else "")
            )

    chats = get_chats_with_user_messages(request.user).distinct()
    is_admin = chat.admins.filter(id=request.user.id).exists()
    pinned_messages = chat.pinned_messages.select_related(
        "sender",
        "sender__profile",
        "poll"
    ).prefetch_related(
        Prefetch(
            "attachments",
            queryset=MessageAttachment.objects.order_by("id"),
            to_attr="prefetched_attachments"
        )
    ).order_by("created_at")
    pinned_message_ids = set(pinned_messages.values_list("id", flat=True))

    for pinned_message in pinned_messages:
        poll = getattr(pinned_message, "poll", None)
        attachment = pinned_message.prefetched_attachments[0] if pinned_message.prefetched_attachments else None

        pinned_message.pinned_text = (
            pinned_message.text
            or (poll.title if poll else "")
            or (attachment.file.name if attachment else "")
        )

    context = {
        "chats": chats,
        "active_chat": chat,
        "chat_messages": chat_messages,
        "is_admin": is_admin,
        "pinned_messages": pinned_messages,
        "pinned_message_ids": pinned_message_ids,
        "participant_count": chat.participants.count(),
    }

    return render(request, "Main/Main.html", context)


@login_required(login_url="HomePage")
def send_file(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)

    if request.method == "POST":
        text = request.POST.get("text", "").strip()
        uploaded_file = request.FILES.get("file")

        if uploaded_file:
            message = Message.objects.create(
                chat=chat,
                sender=request.user,
                text=text
            )

            if uploaded_file.content_type.startswith("image/"):
                attachment_type = "image"
            elif uploaded_file.content_type.startswith("video/"):
                attachment_type = "video"
            else: 
                attachment_type = "file"

            MessageAttachment.objects.create(
                message=message,
                file=uploaded_file,
                attachment_type=attachment_type
            )
        
    return redirect("ChatDetail", chat_id=chat.id)


@login_required(login_url="HomePage")
def create_poll(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)

    if not chat.participants.filter(id=request.user.id).exists():
        return redirect("Main")

    if request.method == "POST":
        title = request.POST.get("poll_title", "").strip()
        question = request.POST.get("poll_question", "").strip()
        options = [option.strip() for option in request.POST.getlist("poll_options")]
        
        chat_messages = chat.messages.select_related(
            "sender",
            "sender__profile",
            "reply_to",
            "reply_to__sender",
            "reply_to__sender__profile",
            "reply_to__poll",
            "poll",
        ).prefetch_related(
            Prefetch(
                "attachments",
                queryset=MessageAttachment.objects.order_by("id"),
                to_attr="prefetched_attachments"
            ),
            Prefetch(
                "reply_to__attachments",
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
        for message in chat_messages:
            if hasattr(message, "poll"):
                poll_options = list(message.poll.options.all())
                total_votes = message.poll.votes.count()
                max_percent = 0

                for option in poll_options:
                    option_votes = option.votes.count()
                    option.percent = (option_votes / total_votes) * 100 if total_votes > 0 else 0

                    if option.percent > max_percent:
                        max_percent = option.percent

                leaders_count = sum(1 for option in poll_options if option.percent == max_percent and max_percent > 0)

                for option in poll_options:
                    option.is_leading = leaders_count == 1 and option.percent == max_percent

                message.poll_options = poll_options

            if message.reply_to:
                reply_poll = getattr(message.reply_to, "poll", None)
                reply_attachment = message.reply_to.prefetched_attachments[0] if getattr(message.reply_to, "prefetched_attachments", None) else None

                message.reply_preview_text = (
                    message.reply_to.text
                    or (reply_poll.title if reply_poll and reply_poll.title else "")
                    or (reply_poll.question if reply_poll else "")
                    or (reply_attachment.file.name.split("/")[-1] if reply_attachment else "")
                )

        chats = get_chats_with_user_messages(request.user).distinct()
        is_admin = chat.admins.filter(id=request.user.id).exists()
        pinned_messages = chat.pinned_messages.select_related(
            "sender",
            "sender__profile",
            "poll"
        ).prefetch_related(
            Prefetch(
                "attachments",
                queryset=MessageAttachment.objects.order_by("id"),
                to_attr="prefetched_attachments"
            )
        ).order_by("created_at")
        pinned_message_ids = set(pinned_messages.values_list("id", flat=True))

        for pinned_message in pinned_messages:
            poll = getattr(pinned_message, "poll", None)
            attachment = pinned_message.prefetched_attachments[0] if pinned_message.prefetched_attachments else None

            pinned_message.pinned_text = (
                pinned_message.text
                or (poll.title if poll else "")
                or (attachment.file.name.split("/")[-1] if attachment else "")
            )

        context = {
            "chats": chats,
            "active_chat": chat,
            "chat_messages": chat_messages,
            "is_admin": is_admin,
            "pinned_messages": pinned_messages,
            "pinned_message_ids": pinned_message_ids,
            "participant_count": chat.participants.count(),
            "open_poll_form": True,
        }
    
        if not title or not question or any(not option for option in options):
            messages.error(request, "All field are required")
            return render(request, "Main/Main.html", context)
        if len(options) < 2:
            messages.error(request, "Poll must contains at least 2 options")
            return render(request, "Main/Main.html", context)

        message = Message.objects.create(
            chat=chat,
            sender=request.user,
            text=""
        )

        poll = Poll.objects.create(
            message=message,
            creator=request.user,
            title=title,
            question=question
        )

        for option in options:
            PollOption.objects.create(
                poll=poll,
                text=option
            )

    return redirect("ChatDetail", chat_id=chat.id)


@login_required(login_url="HomePage")
def vote(request, option_id):
    option = get_object_or_404(PollOption, id=option_id)
    poll = option.poll
    chat = poll.message.chat

    if not chat.participants.filter(id=request.user.id).exists():
        return redirect("Main")

    if (
        not PollVote.objects.filter(poll=poll, user=request.user).exists() 
        and not poll.is_closed
        and poll.creator != request.user
    ):
        PollVote.objects.create(
            poll=poll,
            option=option,
            user=request.user
        )

    return redirect("ChatDetail", chat_id=chat.id)


@login_required(login_url="HomePage")
def close_poll(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    chat = poll.message.chat

    if not chat.participants.filter(id=request.user.id).exists():
        return redirect("Main")
    
    if request.method == "POST":
        if poll.creator == request.user:
            poll.is_closed = True
            poll.save()

    return redirect("ChatDetail", chat_id=chat.id)
