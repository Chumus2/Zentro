from django.urls import path
from .views import *


urlpatterns = [
    path("", MainView.as_view(), name="Main"),
    path("chats/<int:chat_id>/", ChatDetailView.as_view(), name="ChatDetail"),
    path("create_chat/", CreateChatView.as_view(), name="CreateChat")
]