# Generated by Django 4.2.11 on 2025-02-17 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modules', '0034_vehicle_driver_multas_licences_driver'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle_driver',
            name='address',
            field=models.TextField(blank=True, max_length=80, null=True, verbose_name='Dirección'),
        ),
        migrations.AddField(
            model_name='vehicle_driver',
            name='serial_number',
            field=models.CharField(blank=True, max_length=15, null=True, verbose_name='Número de telefono'),
        ),
    ]
