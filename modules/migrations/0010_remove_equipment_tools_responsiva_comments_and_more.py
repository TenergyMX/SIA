# Generated by Django 4.2.11 on 2024-08-30 04:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('modules', '0009_equipment_tools_responsiva_comments'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='equipment_tools_responsiva',
            name='comments',
        ),
        migrations.RemoveField(
            model_name='equipment_tools_responsiva',
            name='document_equipment',
        ),
    ]