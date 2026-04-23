from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
import csv

from .models import User
from .forms import UserImportForm


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    fieldsets = UserAdmin.fieldsets + (
        ("DataCapture Fields", {
            "fields": ("role", "pin", "must_change_pin"),
        }),
    )

    list_display = ("username", "role", "must_change_pin", "is_staff")

    # URL for import
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "import-users/",
                self.admin_site.admin_view(self.import_users),
                name="accounts_user_import",
            ),
        ]
        return custom_urls + urls

    # Import logic
    def import_users(self, request):
        if request.method == "POST":
            form = UserImportForm(request.POST, request.FILES)

            if form.is_valid():
                file = form.cleaned_data["csv_file"]
                decoded = file.read().decode("utf-8").splitlines()
                reader = csv.DictReader(decoded)

                count = 0

                for row in reader:
                    if not row.get("username"):
                        continue

                    User.objects.create(
                        username=row["username"],
                        role=row.get("role", "capturer"),
                        pin=make_password(row.get("pin", "1234")),
                        must_change_pin=True,
                        is_staff=True,
                    )
                    count += 1

                messages.success(request, f"{count} users imported successfully!")
                return redirect("../")

        else:
            form = UserImportForm()

        return render(request, "admin/import_users.html", {"form": form})

    # 🔥 THIS ADDS BUTTON CONTEXT
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["import_url"] = "import-users/"
        return super().changelist_view(request, extra_context=extra_context)