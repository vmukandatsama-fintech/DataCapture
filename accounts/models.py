from django.contrib.auth.models import AbstractUser
from django.db import models


class Grower(models.Model):
    """
    Reference table for CY26 Growers.
    Sourced from CY26_Masterlist_18_02_2026.csv
    """

    # ── Grower Identity ───────────────────────────────────────────────────────
    grower_id = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="Grower ID",
        help_text="e.g. V102398",
    )
    grower_name = models.CharField(max_length=50, verbose_name="Grower Name")
    timb_name = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="TIMB Name"
    )
    master_id = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="Master ID"
    )
    timb_id = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="TIMB ID"
    )

    # ── Classification ────────────────────────────────────────────────────────
    class SchemeChoices(models.TextChoices):
        A = "A Scheme", "A Scheme"
        B = "B Scheme", "B Scheme"
        D = "D Scheme", "D Scheme"
        R = "R Scheme", "R Scheme"

    scheme = models.CharField(
        max_length=10,
        choices=SchemeChoices.choices,
        verbose_name="Scheme",
    )
    cy26_ha = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="CY26 Hectares",
    )
    stop_order_number = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="Stop Order #"
    )
    contract_status = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="Contract Status"
    )

    # ── Area ──────────────────────────────────────────────────────────────────
    area_code = models.IntegerField(verbose_name="Area Code")
    area = models.CharField(max_length=20, verbose_name="Area")

    # ── Group ─────────────────────────────────────────────────────────────────
    group_code = models.IntegerField(verbose_name="Group Code")
    group_name = models.CharField(max_length=30, verbose_name="Group")

    # ── Manager ───────────────────────────────────────────────────────────────
    manager_code = models.IntegerField(verbose_name="Manager Code")
    manager = models.CharField(max_length=30, verbose_name="Manager")

    # ── Area Manager ──────────────────────────────────────────────────────────
    area_manager_code = models.IntegerField(verbose_name="Area Manager Code")
    area_manager = models.CharField(max_length=30, verbose_name="Area Manager")

    # ── Leaf Technician ───────────────────────────────────────────────────────
    ltech_code = models.IntegerField(verbose_name="Leaf Technician Code")
    ltech = models.CharField(max_length=30, verbose_name="Leaf Technician")

    # ── Biometrics ────────────────────────────────────────────────────────────
    class BiometricsChoices(models.TextChoices):
        ENROLLED = "Enrolled", "Enrolled"
        NOT_ENROLLED = "Not Enrolled", "Not Enrolled"

    biometrics = models.CharField(
        max_length=20,
        choices=BiometricsChoices.choices,
        blank=True,
        null=True,
        verbose_name="Biometrics",
    )

    # ── TIMB Financial ────────────────────────────────────────────────────────
    timb_stop_order_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="TIMB Stop Order Value",
    )

    class Meta:
        db_table = "grower"
        verbose_name = "Grower"
        verbose_name_plural = "Growers"
        ordering = ["grower_id"]
        indexes = [
            models.Index(fields=["scheme"], name="idx_grower_scheme"),
            models.Index(fields=["area_code"], name="idx_grower_area"),
            models.Index(fields=["group_code"], name="idx_grower_group"),
            models.Index(fields=["manager_code"], name="idx_grower_manager"),
            models.Index(fields=["area_manager_code"], name="idx_grower_area_manager"),
        ]

    def __str__(self):
        return f"{self.grower_id} — {self.grower_name}"


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