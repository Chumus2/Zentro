from django.urls import path
from .views import EditChatView


urlpatterns = [
    path("edit/<int:chat_id>/", EditChatView.as_view(), name="EditChat")
]