from django.urls import path
from .views import SignUpView, SignInView


urlpatterns = [
    path("signup/", SignUpView.as_view(), name="SignUp"),
    path("signin/", SignInView.as_view(), name="SignIn")
]