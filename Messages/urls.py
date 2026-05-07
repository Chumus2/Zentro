from django.urls import path
from . import views


urlpatterns = [
    path("delete_message/<int:message_id>/", views.delete_message, name="DeleteMessage")
]