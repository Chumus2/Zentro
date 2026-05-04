from django.urls import path
from .views import EditChatView, ChatParticipantsView


urlpatterns = [
    path("edit/<int:chat_id>/", EditChatView.as_view(), name="EditChat"),
    path("participants/<int:chat_id>/", ChatParticipantsView.as_view(), name="Participants")
]