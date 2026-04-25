"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from datetime import date


def _ctx():
    return {'year': date.today().year}


def home(request):
    return render(request, 'home.html', _ctx())


def login_page(request):
    return render(request, 'auth/login.html', _ctx())


def change_pin_page(request):
    return render(request, 'auth/change_pin.html', _ctx())


def dashboard(request):
    return render(request, 'dashboard.html', _ctx())


def growers_list(request):
    return render(request, 'growers/list.html', _ctx())


def grower_detail(request, grower_id):
    return render(request, 'growers/detail.html', _ctx())


def truck_deliveries_page(request):
    return render(request, 'trucks/list.html', _ctx())


def rejected_bales_page(request):
    return render(request, 'rejected_bales/list.html', _ctx())


def releases_page(request):
    return render(request, 'releases/list.html', _ctx())


urlpatterns = [
    path('', home, name='home'),
    path('login/', login_page, name='login'),
    path('change-pin/', change_pin_page, name='change-pin'),
    path('dashboard/', dashboard, name='dashboard'),
    path('growers/', growers_list, name='growers'),
    path('growers/<str:grower_id>/', grower_detail, name='grower-detail'),
    path('trucks/', truck_deliveries_page, name='trucks'),
    path('rejected-bales/', rejected_bales_page, name='rejected-bales'),
    path('releases/', releases_page, name='releases'),
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
]
