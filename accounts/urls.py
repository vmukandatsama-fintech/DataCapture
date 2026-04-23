from django.urls import path
from .views import LoginView, ChangePinView

urlpatterns = [
    path("login/", LoginView.as_view()),
    path("change-pin/", ChangePinView.as_view()),
]