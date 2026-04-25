from django.db import migrations


FLOORS = [
    ("BAY 14 A", "Harare"),
    ("BAY 14 B", "Harare"),
    ("COMMERCIAL", "Harare"),
    ("ETHICAL", "Harare"),
    ("ETHICAL KAROI", "Karoi"),
    ("ETHICAL MARONDERA", "Karoi"),
    ("ETHICAL MVURWI", "Mvurwi"),
    ("GLOBAL LEAF", "Mvurwi"),
    ("GLOBAL LEAF KAROI", "Karoi"),
    ("GLOBAL LEAF RUSAPE", "Rusape"),
    ("MUNAKIRI", "Harare"),
    ("MUNAKIRI HARARE", "Harare"),
    ("MUNAKIRI RUSAPE", "Rusape"),
    ("NEW COMMERCIAL", "Harare"),
    ("SHASHA", "Harare"),
    ("SHASHA KAROI", "Karoi"),
    ("SHASHA MARONDERA", "Marondera"),
    ("SHASHA MVURWI", "Mvurwi"),
    ("TSF AUCTION A", "Harare"),
    ("TSF AUCTION B", "Harare"),
    ("TSF CONTRACT", "Harare"),
]

CLASSIFICATIONS = [
    ("BMR", "Mixed leaves in the hands"),
    ("BGR", "Badly handled (too wet or too dry)"),
    ("DR", "Damaged oil, grease, paraffin, soot etc."),
    ("KR", "Funked"),
    ("LR", "Mouldy"),
    ("MR", "Mixed hands of tobacco"),
    ("NDR", "Undeclared split"),
    ("NE", "Nesting"),
    ("NGU", "Tobacco which is unsound and not fit for sale (withdrawal by TIMB)"),
    ("NR", "No sale (Ticket Marker)"),
    ("NTRM", "Non Tobacco Related Material"),
    ("OR", "Hot"),
    ("RR", "Overweight, underweight, oversize or other reason"),
    ("SR", "Stem rot"),
    ("TA", "Torn against"),
    ("TT", "Torn against price"),
    ("US", "Destroy (withdrawn by growers' representative)"),
    ("WR", "Withdrawn for any other reason"),
]


def seed_data(apps, schema_editor):
    Floor = apps.get_model('accounts', 'Floor')
    RejectionClassification = apps.get_model('accounts', 'RejectionClassification')
    for name, location in FLOORS:
        Floor.objects.get_or_create(name=name, defaults={'location': location})
    for code, description in CLASSIFICATIONS:
        RejectionClassification.objects.get_or_create(code=code, defaults={'description': description})


def unseed_data(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_floor_rejectionclassification_rejectedbale'),
    ]

    operations = [
        migrations.RunPython(seed_data, unseed_data),
    ]
