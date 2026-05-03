from django.urls import path
from .views import MainView, ChatDetailView


urlpatterns = [
    path("", MainView.as_view(), name="Main"),
    path("chats/<int:chat_id>/", ChatDetailView.as_view(), name="ChatDetail")
]