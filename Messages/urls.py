from django.urls import path
from . import views


urlpatterns = [
    path("delete_message/<int:message_id>/", views.delete_message, name="DeleteMessage"),
    path("pin/message/<int:message_id>/", views.pin_message, name="PinMessage"),
    path("unpin/message/<int:message_id>/", views.unpin_message, name="UnpinMessage"),
    path("edit_message/<int:message_id>/", views.edit_message, name="EditMessage"),
    path("reply_to_message/<int:chat_id>/", views.reply_to_message, name="ReplyToMessage"),
    path("send_file/<int:chat_id>/", views.send_file, name="SendFile"),
    path("create_poll/<int:chat_id>/", views.create_poll, name="CreatePoll"),
    path("vote/<int:option_id>/", views.vote, name="Vote")
]