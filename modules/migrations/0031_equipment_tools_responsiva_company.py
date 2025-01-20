# Generated by Django 4.2.11 on 2024-10-22 18:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        ('modules', '0030_equipment_tools_company'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipment_tools_responsiva',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.company', verbose_name='Empresa'),
        ),
        migrations.CreateModel(
            name='Services',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_service', models.CharField(blank=True, default='Regular', max_length=50, null=True, verbose_name='Nombre servicio')),
                ('description_service', models.TextField(blank=True, null=True, verbose_name='Descripcion Servicio')),
                ('start_date_service', models.DateField(blank=True, null=True, verbose_name='Fecha de inicio')),
                ('time_quantity_service', models.PositiveIntegerField(blank=True, default=1, null=True, verbose_name='Cantidad de Tiempo')),
                ('time_unit_service', models.CharField(blank=True, choices=[('day', 'Día(s)'), ('month', 'Mes(es)'), ('year', 'Año(s)')], max_length=50, null=True, verbose_name='Unidad de Tiempo')),
                ('price_service', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10, null=True, verbose_name='Cantidad de servicios')),
                ('category_service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='modules.services_category', verbose_name='Categoría de servicios')),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.company', verbose_name='Empresa')),
                ('provider_service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.provider', verbose_name='Proveedor')),
            ],
        ),
        migrations.CreateModel(
            name='Payments_Services',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('proof_payment', models.FileField(blank=True, null=True, upload_to='docs/', verbose_name='Comprobante de pago')),
                ('total_payment', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10, null=True, verbose_name='Costo')),
                ('next_date_payment', models.DateField(blank=True, null=True, verbose_name='Próxima fecha de pago')),
                ('status_payment', models.CharField(choices=[('pending', 'Pendiente'), ('upcoming', 'Próximo'), ('unpaid', 'No Pagado'), ('paid', 'Pagado')], default='pending', max_length=10, verbose_name='Estado de pago')),
                ('name_service_payment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='modules.services', verbose_name='Nombre del servicio')),
            ],
        ),
        migrations.CreateModel(
            name='Services_Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_category', models.CharField(blank=True, max_length=100, null=True, verbose_name='Nombre')),
                ('short_name_category', models.CharField(blank=True, max_length=50, null=True, verbose_name='Nombre Corto')),
                ('is_active_category', models.BooleanField(default=True, verbose_name='¿Está Activo?')),
                ('description_category', models.TextField(blank=True, null=True, verbose_name='Descripción')),
            ],
        ),
        migrations.CreateModel(
            name='Plans',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date_plan', models.DateField(blank=True, null=True, verbose_name='Fecha de inicio')),
                ('type_plan', models.CharField(choices=[('basic', 'Basico'), ('advanced', 'Avanzado'), ('premium', 'Premium')], default='pending', max_length=10, verbose_name='Tipo de plan')),
                ('status_payment_plan', models.BooleanField(default=False, verbose_name='Estado de pago')),
                ('time_quantity_plan', models.PositiveIntegerField(blank=True, default=1, null=True, verbose_name='Cantidad de Tiempo')),
                ('time_unit_plan', models.CharField(blank=True, choices=[('day', 'Día(s)'), ('month', 'Mes(es)'), ('year', 'Año(s)')], max_length=50, null=True, verbose_name='Unidad de Tiempo')),
                ('end_date_plan', models.DateField(blank=True, null=True, verbose_name='Fecha de fin')),
                ('total', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10, null=True, verbose_name='Costo\xa0total')),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.company', verbose_name='Empresa')),
                ('module', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.module', verbose_name='Módulos')),
            ],
        ),
    ]
