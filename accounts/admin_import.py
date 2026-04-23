import csv
from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .models import User


def import_users(modeladmin, request, queryset):
    # placeholder for admin action hook
    pass


@admin.action(description="Import Users from CSV (upload via admin form)")
def import_users_csv(modeladmin, request, queryset):
    # This will be replaced by custom view (next step)
    messages.info(request, "Use the Import Users button in admin.")