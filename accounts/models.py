from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ("capturer", "Capturer"),
        ("supervisor", "Supervisor"),
        ("admin", "Admin"),
    ]

    pin = models.CharField(max_length=128)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    must_change_pin = models.BooleanField(default=True)

    def __str__(self):
        return self.username