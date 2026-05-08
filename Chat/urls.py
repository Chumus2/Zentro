from django.urls import path
from .views import *


urlpatterns = [
    path("edit/<int:chat_id>/", EditChatView.as_view(), name="EditChat"),
    path("participants/<int:chat_id>/", ChatParticipantsView.as_view(), name="Participants"),
    path("add_user/<int:chat_id>/", add_participant, name="AddUser"),
    path("remove_user/<int:chat_id>/", remove_participant, name="RemoveUser"),
    path("leave/<int:chat_id>/", participant_leave, name="LeaveUser"),
]