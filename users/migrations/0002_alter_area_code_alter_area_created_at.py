# Generated by Django 4.2.11 on 2024-12-12 21:56

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='area',
            name='code',
            field=models.CharField(blank=True, help_text='Código único para identificar el área', max_length=10, null=True, verbose_name='Código del Área'),
        ),
        migrations.AlterField(
            model_name='area',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Fecha de Creación'),
        ),
    ]
