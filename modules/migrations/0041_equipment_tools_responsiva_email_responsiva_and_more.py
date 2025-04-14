# Generated by Django 4.2.11 on 2025-03-28 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modules', '0040_alter_computersystem_identifier'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipment_tools_responsiva',
            name='email_responsiva',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='payments_services',
            name='email_payment',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='vehicle_audit',
            name='email_audit',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='vehicle_insurance',
            name='email_insurance',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='vehicle_maintenance',
            name='email_maintenance',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='vehicle_refrendo',
            name='email_refrendo',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='vehicle_tenencia',
            name='email_tenencia',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='vehicle_verificacion',
            name='email_verificacion',
            field=models.BooleanField(default=False),
        )
    ]
