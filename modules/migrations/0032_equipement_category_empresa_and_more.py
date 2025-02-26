# Generated by Django 4.2.11 on 2025-01-19 23:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_area_code_alter_area_created_at'),
        ('modules', '0031_equipment_tools_responsiva_company'),
    ]

    operations = [

        migrations.AlterField(
            model_name='infrastructure_category',
            name='name',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='Nombre'),
        ),
        migrations.AlterField(
            model_name='infrastructure_category',
            name='short_name',
            field=models.CharField(blank=True, max_length=48, null=True, verbose_name='Nombre Corto'),
        ),
        migrations.AddField(
            model_name='services_category',
            name='empresa',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.company', verbose_name='Empresa'),
        ),
    ]
