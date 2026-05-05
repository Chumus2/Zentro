from django.urls import path
from .views import *


urlpatterns = [
    path("", MainView.as_view(), name="Main"),
    path("chats/<int:chat_id>/", ChatDetailView.as_view(), name="ChatDetail"),
    path("leave/<int:chat_id>/", ParticipantLeaveView.as_view(), name="LeaveUser")
]