# Generated by Django 4.2.11 on 2024-09-09 15:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        ('modules', '0016_alter_equipement_category_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equipment_tools',
            name='equipment_area',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.area', verbose_name='Área'),
        ),
        migrations.AlterField(
            model_name='equipment_tools',
            name='equipment_brand',
            field=models.CharField(default='Regular', max_length=50, verbose_name='Marca'),
        ),
        migrations.AlterField(
            model_name='equipment_tools',
            name='equipment_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='modules.equipement_category', verbose_name='Categoría'),
        ),
        migrations.AlterField(
            model_name='equipment_tools',
            name='equipment_description',
            field=models.CharField(default='Regular', max_length=50, verbose_name='Descripción'),
        ),
        migrations.AlterField(
            model_name='equipment_tools',
            name='equipment_location',
            field=models.CharField(default='Regular', max_length=50, verbose_name='Ubicación'),
        ),
        migrations.AlterField(
            model_name='equipment_tools',
            name='equipment_name',
            field=models.CharField(default='Regular', max_length=50, verbose_name='Nombre equipo'),
        ),
        migrations.AlterField(
            model_name='equipment_tools',
            name='equipment_technical_sheet',
            field=models.FileField(blank=True, null=True, upload_to='docs/Equipments_tools', verbose_name='Ficha técnica'),
        ),
        migrations.AlterField(
            model_name='equipment_tools',
            name='equipment_type',
            field=models.CharField(default='Regular', max_length=50, verbose_name='Tipo de equipo'),
        ),
    ]
