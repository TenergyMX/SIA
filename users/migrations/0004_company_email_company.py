# Generated by Django 4.2.11 on 2025-04-24 22:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_remove_submodule_short_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='email_company',
            field=models.BooleanField(default=False),
        ),
    ]
