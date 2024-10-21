# Generated by Django 4.2.11 on 2024-10-18 22:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        ('modules', '0029_alter_equipment_tools_equipment_description_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipment_tools',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.company', verbose_name='Empresa'),
        ),
    ]
