# Generated by Django 4.2.11 on 2024-09-18 18:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        ('modules', '0023_remove_equipment_tools_equipment_location'),
    ]

    operations = [
        migrations.CreateModel(
            name='Equipmets_Tools_locations',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location_name', models.CharField(blank=True, max_length=50, null=True, verbose_name='Nombre')),
                ('location_status', models.BooleanField(default=True, verbose_name='¿Está activa la ubicación?')),
                ('location_company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.company')),
            ],
        ),
    ]