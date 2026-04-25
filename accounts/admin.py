from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.db import transaction
from unfold.admin import ModelAdmin as UnfoldModelAdmin
import csv
import re

from .models import User, Grower, Floor, RejectionClassification, RejectedBale, ReleaseFromHold
from .forms import UserImportForm, GrowerImportForm, AdminUserCreationForm


@admin.register(User)
class CustomUserAdmin(UnfoldModelAdmin, UserAdmin):
    model = User
    add_form = AdminUserCreationForm

    add_fieldsets = (
        (None, {
            "fields": ("username", "role", "pin", "pin_confirm", "is_staff", "must_change_pin"),
        }),
    )

    fieldsets = UserAdmin.fieldsets + (
        ("DataCapture Fields", {
            "fields": ("role", "pin", "must_change_pin"),
        }),
    )

    list_display = ("username", "role", "must_change_pin", "is_staff")

    def save_model(self, request, obj, form, change):
        if not change and isinstance(form, AdminUserCreationForm):
            # PIN already hashed by AdminUserCreationForm.save(); bypass UserAdmin password logic
            obj.save()
        else:
            super().save_model(request, obj, form, change)

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

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["import_url"] = "import-users/"
        return super().changelist_view(request, extra_context=extra_context)


# ── Grower column header normaliser ──────────────────────────────────────────

def _norm(s):
    return re.sub(r'[\s_\-#]+', '', s).lower()


_SENTENCE_CASE_FIELDS = {
    'grower_name', 'timb_name', 'master_id', 'timb_id',
    'area', 'group_name', 'manager', 'area_manager', 'ltech',
    'stop_order_number', 'contract_status', 'biometrics',
}


# Maps normalised CSV header → (model_field, type_converter)
_GROWER_COLUMN_MAP = {
    'growerid':          ('grower_id',            str),
    'growerno':          ('grower_id',            str),
    'growername':        ('grower_name',          str),
    'timbname':          ('timb_name',            str),
    'masterid':          ('master_id',            str),
    'timbid':            ('timb_id',              str),
    'scheme':            ('scheme',               str),
    'cy26ha':            ('cy26_ha',              lambda v: float(v) if v else None),
    'cy26hectares':      ('cy26_ha',              lambda v: float(v) if v else None),
    'hectares':          ('cy26_ha',              lambda v: float(v) if v else None),
    'ha':                ('cy26_ha',              lambda v: float(v) if v else None),
    'stopordernumber':   ('stop_order_number',    str),
    'stoporder':         ('stop_order_number',    str),
    'contractstatus':    ('contract_status',      str),
    'status':            ('contract_status',      str),
    'areacode':          ('area_code',            int),
    'area':              ('area',                 str),
    'groupcode':         ('group_code',           int),
    'groupname':         ('group_name',           str),
    'group':             ('group_name',           str),
    'managercode':       ('manager_code',         int),
    'manager':           ('manager',              str),
    'areamanagercode':   ('area_manager_code',    int),
    'areamanager':       ('area_manager',         str),
    'am':                ('area_manager',         str),
    'amcode':            ('area_manager_code',    int),
    'ltechcode':              ('ltech_code', int),
    'leadtechcode':           ('ltech_code', int),
    'leaftechcode':           ('ltech_code', int),
    'leaftechniciancode':     ('ltech_code', int),
    'ltech':                  ('ltech',      str),
    'leadtechnician':         ('ltech',      str),
    'leaftechnician':         ('ltech',      str),
    'biometrics':             ('biometrics', str),
    'timbstopordervalue':     ('timb_stop_order_value', lambda v: float(v) if v else None),
    'stopordervalue':    ('timb_stop_order_value', lambda v: float(v) if v else None),
}


@admin.register(Grower)
class GrowerAdmin(UnfoldModelAdmin):
    list_display = (
        'grower_id', 'grower_name', 'scheme', 'area',
        'group_name', 'manager', 'cy26_ha', 'contract_status', 'biometrics',
    )
    list_filter = ('scheme', 'area', 'group_name', 'contract_status', 'biometrics')
    search_fields = ('grower_id', 'grower_name', 'timb_name', 'timb_id')
    ordering = ('grower_id',)
    list_per_page = 50

    fieldsets = (
        ('Identity', {
            'fields': ('grower_id', 'grower_name', 'timb_name', 'master_id', 'timb_id'),
        }),
        ('Classification', {
            'fields': ('scheme', 'cy26_ha', 'stop_order_number', 'contract_status', 'biometrics'),
        }),
        ('Area & Group', {
            'fields': ('area_code', 'area', 'group_code', 'group_name'),
        }),
        ('Personnel', {
            'fields': (
                'manager_code', 'manager',
                'area_manager_code', 'area_manager',
                'ltech_code', 'ltech',
            ),
        }),
        ('TIMB Financial', {
            'fields': ('timb_stop_order_value',),
        }),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'import-growers/',
                self.admin_site.admin_view(self.import_growers),
                name='accounts_grower_import',
            ),
            path(
                'import-growers/sample.csv',
                self.admin_site.admin_view(self.sample_csv),
                name='accounts_grower_sample_csv',
            ),
        ]
        return custom_urls + urls

    def sample_csv(self, request):
        import io
        from django.http import HttpResponse

        headers = [
            'Grower ID', 'Grower Name', 'TIMB Name', 'Master ID', 'TIMB ID',
            'Scheme', 'CY26 Ha', 'Stop Order #', 'Contract Status',
            'Area Code', 'Area', 'Group Code', 'Group', 'Manager Code', 'Manager',
            'Area Manager Code', 'Area Manager', 'Leaf Technician Code', 'Leaf Technician',
            'TIMB Stop Order Value', 'Biometrics',
        ]
        rows = [
            [
                'V102398', 'JOHN MOYO', 'J MOYO', 'M001', 'T001',
                'A Scheme', '2.50', 'SO-001', 'Active',
                '1', 'HARARE', '10', 'HARARE NORTH', '20', 'T SMITH',
                '30', 'R JONES', '40', 'P DUBE',
                '1500.00', 'Enrolled',
            ],
            [
                'V102399', 'JANE MUTASA', '', '', '',
                'B Scheme', '1.75', '', 'Active',
                '1', 'HARARE', '10', 'HARARE NORTH', '20', 'T SMITH',
                '30', 'R JONES', '40', 'P DUBE',
                '', 'Not Enrolled',
            ],
        ]

        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(headers)
        writer.writerows(rows)

        response = HttpResponse(buf.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="grower_import_sample.csv"'
        return response

    def import_growers(self, request):
        if request.method == 'POST':
            form = GrowerImportForm(request.POST, request.FILES)
            if form.is_valid():
                file = form.cleaned_data['csv_file']
                try:
                    decoded = file.read().decode('utf-8-sig').splitlines()
                except UnicodeDecodeError:
                    file.seek(0)
                    decoded = file.read().decode('latin-1').splitlines()

                reader = csv.DictReader(decoded)
                headers = reader.fieldnames or []
                col_map = {}
                for h in headers:
                    key = _norm(h)
                    if key in _GROWER_COLUMN_MAP:
                        col_map[h] = _GROWER_COLUMN_MAP[key]

                created = updated = skipped = 0
                errors = []

                with transaction.atomic():
                    for i, row in enumerate(reader, start=2):
                        # Resolve grower_id
                        grower_id = None
                        for h, (field, conv) in col_map.items():
                            if field == 'grower_id':
                                raw = row.get(h, '').strip()
                                grower_id = raw if raw else None
                                break

                        if not grower_id:
                            skipped += 1
                            continue

                        defaults = {}
                        for h, (field, conv) in col_map.items():
                            if field == 'grower_id':
                                continue
                            raw = row.get(h, '').strip()
                            try:
                                value = conv(raw) if raw else None
                                if isinstance(value, str) and field in _SENTENCE_CASE_FIELDS:
                                    value = value.title()
                                defaults[field] = value
                            except (ValueError, TypeError) as e:
                                errors.append(f"Row {i}: {field} — {e}")

                        # Required integer fields default to 0 if missing
                        for int_field in ('area_code', 'group_code', 'manager_code',
                                          'area_manager_code', 'ltech_code'):
                            if defaults.get(int_field) is None:
                                defaults[int_field] = 0

                        # Required string fields default to empty string if missing
                        for str_field in ('area', 'group_name', 'manager',
                                          'area_manager', 'ltech', 'scheme'):
                            if defaults.get(str_field) is None:
                                defaults[str_field] = ''

                        _, was_created = Grower.objects.update_or_create(
                            grower_id=grower_id,
                            defaults=defaults,
                        )
                        if was_created:
                            created += 1
                        else:
                            updated += 1

                summary = f"{created} created, {updated} updated, {skipped} skipped."
                if errors:
                    messages.warning(request, f"Import complete with issues: {summary} Errors: {'; '.join(errors[:5])}")
                else:
                    messages.success(request, f"Import successful — {summary}")
                return redirect('../')
        else:
            form = GrowerImportForm()

        column_info = [
            {'headers': 'Grower ID, Grower No',             'field': 'grower_id',            'required': 'Yes'},
            {'headers': 'Grower Name',                       'field': 'grower_name',          'required': 'Yes'},
            {'headers': 'Scheme',                            'field': 'scheme',               'required': 'Yes'},
            {'headers': 'Area Code',                         'field': 'area_code',            'required': 'Yes'},
            {'headers': 'Area',                              'field': 'area',                 'required': 'Yes'},
            {'headers': 'Group Code',                        'field': 'group_code',           'required': 'Yes'},
            {'headers': 'Group, Group Name',                 'field': 'group_name',           'required': 'Yes'},
            {'headers': 'Manager Code',                      'field': 'manager_code',         'required': 'Yes'},
            {'headers': 'Manager',                           'field': 'manager',              'required': 'Yes'},
            {'headers': 'Area Manager Code, AM Code',        'field': 'area_manager_code',    'required': 'Yes'},
            {'headers': 'Area Manager, AM',                  'field': 'area_manager',         'required': 'Yes'},
            {'headers': 'Leaf Technician Code, LTech Code',   'field': 'ltech_code',           'required': 'Yes'},
            {'headers': 'Leaf Technician, LTech',            'field': 'ltech',                'required': 'Yes'},
            {'headers': 'CY26 Ha, CY26 Hectares, Ha',        'field': 'cy26_ha',              'required': 'No'},
            {'headers': 'TIMB Name',                         'field': 'timb_name',            'required': 'No'},
            {'headers': 'TIMB ID',                           'field': 'timb_id',              'required': 'No'},
            {'headers': 'Master ID',                         'field': 'master_id',            'required': 'No'},
            {'headers': 'Stop Order #, Stop Order Number',   'field': 'stop_order_number',    'required': 'No'},
            {'headers': 'Contract Status, Status',           'field': 'contract_status',      'required': 'No'},
            {'headers': 'TIMB Stop Order Value',             'field': 'timb_stop_order_value','required': 'No'},
            {'headers': 'Biometrics',                        'field': 'biometrics',           'required': 'No'},
        ]
        return render(request, 'admin/import_growers.html', {'form': form, 'column_info': column_info})

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['import_url'] = 'import-growers/'
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(Floor)
class FloorAdmin(UnfoldModelAdmin):
    list_display = ('name', 'location')
    search_fields = ('name', 'location')
    ordering = ('name',)


@admin.register(RejectionClassification)
class RejectionClassificationAdmin(UnfoldModelAdmin):
    list_display = ('code', 'description')
    search_fields = ('code', 'description')
    ordering = ('code',)


@admin.register(ReleaseFromHold)
class ReleaseFromHoldAdmin(UnfoldModelAdmin):
    list_display = ('resolution_date', 'ticket_number', 'resolution', 'reference', 'floor', 'created_by')
    list_filter = ('resolution_date', 'resolution', 'floor')
    search_fields = ('ticket_number', 'reference')
    ordering = ('-resolution_date',)
    date_hierarchy = 'resolution_date'


@admin.register(RejectedBale)
class RejectedBaleAdmin(UnfoldModelAdmin):
    list_display = ('date', 'floor', 'grower_number', 'grower_name', 'ticket_number', 'lot_number', 'group_number', 'classification', 'created_by')
    list_filter = ('date', 'floor', 'classification')
    search_fields = ('grower_number', 'grower_name', 'ticket_number')
    ordering = ('-date',)
    date_hierarchy = 'date'
