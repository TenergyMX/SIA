# Generated by Django 4.2.11 on 2024-08-15 18:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('modules', '0002_equipement_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='Equipment_Tools',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('equipment_name', models.CharField(blank=True, default='Regular', max_length=50, null=True, verbose_name='Nombre equipo')),
                ('equipment_type', models.CharField(blank=True, default='Regular', max_length=50, null=True, verbose_name='tipo de equipo')),
                ('equipment_brand', models.CharField(blank=True, default='Regular', max_length=50, null=True, verbose_name='Marca')),
                ('equipment_description', models.CharField(blank=True, default='Regular', max_length=50, null=True, verbose_name='Descripcion')),
                ('cost', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10, null=True, verbose_name='Costo')),
                ('amount', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=4, null=True, verbose_name='Cantidad')),
                ('equipment_technical_sheet', models.FileField(blank=True, null=True, upload_to='docs/', verbose_name='Ficha tecnica')),
                ('equipment_area', models.CharField(blank=True, default='Regular', max_length=50, null=True, verbose_name='Area_pertenece')),
                ('equipment_responsible', models.CharField(blank=True, default='Regular', max_length=50, null=True, verbose_name='Responsable')),
                ('equipment_location', models.CharField(blank=True, default='Regular', max_length=50, null=True, verbose_name='Ubicacion')),
                ('equipment_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='modules.equipement_category', verbose_name='Categoria')),
            ],
        ),
    ]
