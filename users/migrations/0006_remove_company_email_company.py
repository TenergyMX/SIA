# Generated by Django 4.2.11 on 2025-04-25 17:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_company_email_company'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='company',
            name='email_company',
        ),
    ]
