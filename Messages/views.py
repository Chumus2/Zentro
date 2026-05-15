from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from Main.models import Message, Chat, MessageAttachment, Poll, PollOption


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

    Message.objects.create(
        chat=chat,
        sender=None,
        text=f"Message ({message.text}) have been pinned",
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

    Message.objects.create(
        chat=chat,
        sender=None,
        text=f"Message ({message.text}) have been unpinned",
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
        
    chat_messages = chat.messages.order_by("created_at")
    context = {
        "active_chat": chat,
        "chat_messages": chat_messages
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
        
    return redirect("ChatDetail", chat.id)


@login_required(login_url="HomePage")
def create_poll(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)

    if request.method == "POST":
        title = request.POST.get("poll_title", "").strip()
        question = request.POST.get("poll_question", "").strip()
        options = [option.strip() for option in request.POST.getlist("poll_options")]
        chat_messages = chat.messages.order_by("created_at")

        context = {
            "active_chat": chat,
            "chat_messages": chat_messages
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
            title=title,
            question=question
        )

        for option in options:
            PollOption.objects.create(
                poll=poll,
                text=option
            )

    return redirect("ChatDetail", chat.id)
