# Generated by Django 4.2.11 on 2025-05-20 05:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modules', '0061_remove_infrastructure_maintenance_record_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='infrastructure_maintenance',
            name='comprobante',
            field=models.FileField(blank=True, help_text='Comprobante de pago o de matenimiento', null=True, upload_to='docs/'),
        ),
    ]
