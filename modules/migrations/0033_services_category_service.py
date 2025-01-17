# Generated by Django 4.2.11 on 2025-01-09 17:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('modules', '0032_services_category_services_payments_services'),
    ]

    operations = [
        migrations.AddField(
            model_name='services',
            name='category_service',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='modules.services_category', verbose_name='Categoría de servicios'),
        ),
    ]
