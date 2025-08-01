# Generated by Django 4.2.11 on 2025-06-12 17:05
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('modules', '0054_alter_vehicle_insurance_status'),
        ('modules', '0062_infrastructure_maintenance_comprobante'),
    ]

    operations = [
                migrations.CreateModel(
            name='StripeProducts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=254, null=True)),
                ('stripedID', models.CharField(blank=True, max_length=44)),
                ('description', models.CharField(blank=True, max_length=254)),
                ('tagPrice', models.DecimalField(decimal_places=2, max_digits=9)),
                ('price', models.DecimalField(decimal_places=0, max_digits=9)),
                ('active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AlterField(
            model_name='multas',
            name='cost',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=50, null=True, verbose_name='Costo'),
        ),
        migrations.AlterField(
            model_name='plans',
            name='type_plan',
            field=models.CharField(choices=[('basic', 'Basico'), ('advanced', 'Avanzado'), ('premium', 'Premium'), ('elite', 'Elite'), ('esential', 'Esential')], default='pending', max_length=10, verbose_name='Tipo de plan'),
        ),
        migrations.AlterField(
            model_name='vehicle_insurance',
            name='status',
            field=models.CharField(choices=[('PAGADO', 'PAGADO'), ('PROXIMO', 'PROXIMO'), ('VENCIDO', 'VENCIDO'), ('PENDIENTE', 'PENDIENTE'), ('HISTORICO', 'HISTORICO')], default='PROXIMO', max_length=20),
        ),
        migrations.CreateModel(
            name='StripeProducts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=254, null=True)),
                ('stripedID', models.CharField(blank=True, max_length=44)),
                ('description', models.CharField(blank=True, max_length=254)),
                ('tagPrice', models.DecimalField(decimal_places=2, max_digits=9)),
                ('price', models.DecimalField(decimal_places=0, max_digits=9)),
                ('active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        
        migrations.AlterField(
            model_name='multas',
            name='cost',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=50, null=True, verbose_name='Costo'),
        ),
        migrations.AlterField(
            model_name='plans',
            name='type_plan',
            field=models.CharField(choices=[('basic', 'Basico'), ('advanced', 'Avanzado'), ('premium', 'Premium'), ('elite', 'Elite'), ('esential', 'Esential')], default='pending', max_length=10, verbose_name='Tipo de plan'),
        ),
        migrations.AlterField(
            model_name='vehicle_insurance',
            name='status',
            field=models.CharField(choices=[('PAGADO', 'PAGADO'), ('PROXIMO', 'PROXIMO'), ('VENCIDO', 'VENCIDO'), ('PENDIENTE', 'PENDIENTE'), ('HISTORICO', 'HISTORICO')], default='PROXIMO', max_length=20),
        ),
        migrations.CreateModel(
            name='Letter_Facturas_Vehicle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('document_letter_factura', models.FileField(blank=True, null=True, upload_to='docs/', verbose_name='documento de factura')),
                ('vehiculo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='modules.vehicle')),
            ],
        ),

    ]
