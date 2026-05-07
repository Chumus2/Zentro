from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from Main.models import Message, Chat


@login_required(login_url="HomePage")
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    chat = message.chat

    if message.sender != request.user:
        return redirect("ChatDetail", chat_id=chat.id)
    if not chat.participants.filter(id=request.user.id).exists():
        return redirect("Main")
    
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
