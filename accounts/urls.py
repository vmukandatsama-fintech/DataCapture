from django.urls import path
from .views import (
    LoginView, ChangePinView,
    GrowerListView, GrowerDetailView, GrowerLookupView,
    TruckDeliveryListCreateView, TruckDeliveryDetailView, TruckAreaListView,
    FloorListView, RejectionClassificationListView,
    RejectedBaleListCreateView, RejectedBaleDetailView,
    ReleaseFromHoldListCreateView, ReleaseFromHoldDetailView, TicketLookupView,
)

urlpatterns = [
    path("login/", LoginView.as_view()),
    path("change-pin/", ChangePinView.as_view()),
    path("growers/", GrowerListView.as_view()),
    path("growers/lookup/", GrowerLookupView.as_view()),
    path("growers/<str:grower_id>/", GrowerDetailView.as_view()),
    path("truck-deliveries/", TruckDeliveryListCreateView.as_view()),
    path("truck-deliveries/<int:pk>/", TruckDeliveryDetailView.as_view()),
    path("truck-areas/", TruckAreaListView.as_view()),
    path("floors/", FloorListView.as_view()),
    path("rejection-classifications/", RejectionClassificationListView.as_view()),
    path("rejected-bales/", RejectedBaleListCreateView.as_view()),
    path("rejected-bales/<int:pk>/", RejectedBaleDetailView.as_view()),
    path("releases/", ReleaseFromHoldListCreateView.as_view()),
    path("releases/<int:pk>/", ReleaseFromHoldDetailView.as_view()),
    path("ticket-lookup/", TicketLookupView.as_view()),
]
