from django.urls import path
from .views import *


urlpatterns = [
    path("check_profile/<int:user_id>/", ProfilesView.as_view(), name="CheckProfile")
]