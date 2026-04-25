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


class Floor(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Floor Name")
    location = models.CharField(max_length=100, verbose_name="Location")

    class Meta:
        db_table = "floor"
        verbose_name = "Floor"
        verbose_name_plural = "Floors"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.location})"


class RejectionClassification(models.Model):
    code = models.CharField(max_length=10, unique=True, verbose_name="Code")
    description = models.TextField(verbose_name="Description")

    class Meta:
        db_table = "rejection_classification"
        verbose_name = "Rejection Classification"
        verbose_name_plural = "Rejection Classifications"
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} — {self.description}"


class RejectedBale(models.Model):
    date = models.DateField(verbose_name="Date")
    floor = models.ForeignKey(
        Floor, on_delete=models.PROTECT, verbose_name="Floor"
    )
    grower = models.ForeignKey(
        'Grower', on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="Grower"
    )
    grower_number = models.CharField(max_length=20, verbose_name="Grower Number")
    grower_name = models.CharField(max_length=100, blank=True, verbose_name="Grower Name")
    ticket_number = models.CharField(max_length=30, verbose_name="Ticket Number")
    lot_number = models.CharField(max_length=10, verbose_name="Lot Number")
    group_number = models.CharField(max_length=10, verbose_name="Group Number")
    classification = models.ForeignKey(
        RejectionClassification, on_delete=models.PROTECT,
        verbose_name="Classification"
    )

    NTRM_CHOICES = [
        ('DIES', 'DIES'),
        ('F/MATTER', 'F/MATTER'),
        ('F/MATTER - GRASS', 'F/MATTER - GRASS'),
        ('F/MATTER - WIRE', 'F/MATTER - WIRE'),
        ('F/MATTER - PLASTIC', 'F/MATTER - PLASTIC'),
        ('HO', 'HO'),
        ('MDY', 'MDY'),
        ('PAIN', 'PAIN'),
        ('MXD', 'MXD'),
        ('NESTI', 'NESTI'),
        ('OIL', 'OIL'),
        ('STONI', 'STONI'),
        ('WET', 'WET'),
        ('N/A', 'N/A'),
    ]
    ntrm_type = models.CharField(
        max_length=30, blank=True, null=True,
        choices=NTRM_CHOICES, verbose_name="NTRM Type"
    )

    created_by = models.ForeignKey(
        'User', on_delete=models.SET_NULL, null=True,
        related_name='rejected_bales'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "rejected_bale"
        verbose_name = "Rejected Bale"
        verbose_name_plural = "Rejected Bales"
        ordering = ["-date", "floor"]
        indexes = [
            models.Index(fields=["date"], name="idx_bale_date"),
            models.Index(fields=["floor"], name="idx_bale_floor"),
        ]

    def __str__(self):
        return f"{self.date} | {self.floor} | {self.ticket_number}"


class ReleaseFromHold(models.Model):
    RESOLUTION_CHOICES = [
        ('Release to Grower', 'Release to Grower'),
        ('ReOffer', 'ReOffer'),
    ]

    rejected_bale = models.ForeignKey(
        RejectedBale, on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='releases',
        verbose_name="Rejected Bale"
    )
    ticket_number = models.CharField(max_length=30, verbose_name="Bales Ticket Number")
    resolution_date = models.DateField(verbose_name="Resolution Date")
    resolution = models.CharField(
        max_length=30, choices=RESOLUTION_CHOICES, verbose_name="Resolution"
    )
    reference = models.CharField(
        max_length=100, blank=True, null=True,
        verbose_name="Reference (DN / Release No.)"
    )
    floor = models.ForeignKey(
        Floor, on_delete=models.PROTECT, verbose_name="Floor"
    )
    created_by = models.ForeignKey(
        'User', on_delete=models.SET_NULL, null=True, related_name='releases'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "release_from_hold"
        verbose_name = "Release from Hold"
        verbose_name_plural = "Releases from Hold"
        ordering = ["-resolution_date"]
        indexes = [
            models.Index(fields=["resolution_date"], name="idx_release_date"),
            models.Index(fields=["floor"], name="idx_release_floor"),
        ]

    def __str__(self):
        return f"{self.resolution_date} | {self.ticket_number} | {self.resolution}"


class TruckDelivery(models.Model):
    TRANSPORTER_CHOICES = [
        ('Bristan', 'Bristan'),
        ('Staudic', 'Staudic'),
        ('Other', 'Other'),
    ]

    date_expected = models.DateField(verbose_name="Date Expected")
    area = models.CharField(max_length=50, verbose_name="Area")
    transporter = models.CharField(
        max_length=50, choices=TRANSPORTER_CHOICES, verbose_name="Transporter"
    )
    truck_reg = models.CharField(max_length=20, verbose_name="Truck Reg")
    driver_name = models.CharField(max_length=100, verbose_name="Driver Name")
    driver_id = models.CharField(
        max_length=30,
        verbose_name="Driver ID",
        help_text="Format: ##-#######-#-##",
    )
    qty_booked = models.PositiveIntegerField(verbose_name="Qty Booked")
    qty_offloaded = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Qty Offloaded"
    )
    is_booked = models.BooleanField(default=True, verbose_name="Booked")
    created_by = models.ForeignKey(
        'User', on_delete=models.SET_NULL, null=True, related_name='truck_deliveries'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "truck_delivery"
        verbose_name = "Truck Delivery"
        verbose_name_plural = "Truck Deliveries"
        ordering = ["date_expected", "area"]
        indexes = [
            models.Index(fields=["date_expected"], name="idx_truck_date"),
            models.Index(fields=["area"], name="idx_truck_area"),
        ]

    def __str__(self):
        return f"{self.date_expected} | {self.area} | {self.truck_reg}"

    @property
    def difference(self):
        if self.qty_offloaded is not None:
            return self.qty_booked - self.qty_offloaded
        return None


class User(AbstractUser):
    ROLE_CHOICES = [
        ("capturer", "Capturer"),
        ("supervisor", "Supervisor"),
        ("admin", "Admin"),
        ("scaleman", "Scaleman"),
        ("receiver", "Receiver"),
        ("ntrm_classifier", "NTRM Classifier"),
    ]

    pin = models.CharField(max_length=128)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    must_change_pin = models.BooleanField(default=True)

    def __str__(self):
        return self.username
