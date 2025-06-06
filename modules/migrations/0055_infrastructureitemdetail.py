# Generated by Django 4.2.11 on 2025-04-28 18:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_remove_company_email_company'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('modules', '0054_infrastructure_item_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='InfrastructureItemDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('identifier', models.CharField(max_length=255, unique=True)),
                ('assignment_date', models.DateField(blank=True, null=True, verbose_name='Fecha de asignación')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.company')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='details', to='modules.infrastructure_item')),
                ('responsible', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Responsable temporal')),
            ],
            options={
                'verbose_name': 'Detalle de Item de Infraestructura',
                'verbose_name_plural': 'Detalles de Items de Infraestructura',
            },
        ),
    ]
