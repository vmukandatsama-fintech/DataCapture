from django.urls import path
from .views import LoginView, ChangePinView, GrowerListView, GrowerDetailView

urlpatterns = [
    path("login/", LoginView.as_view()),
    path("change-pin/", ChangePinView.as_view()),
    path("growers/", GrowerListView.as_view()),
    path("growers/<str:grower_id>/", GrowerDetailView.as_view()),
]