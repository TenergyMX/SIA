# Generated by Django 4.2.11 on 2025-03-04 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modules', '0034_alter_vehicle_maintenance_kilometer_kilometer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicle',
            name='mileage',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]
