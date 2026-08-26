from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('modules', '0063_merge_20250612_1105'),
        ('users', '0001_initial'),
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

        migrations.CreateModel(
            name='Plans',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date_plan', models.DateField(blank=True, null=True, verbose_name='Fecha de inicio')),
                ('type_plan', models.CharField(
                    choices=[
                        ('basic', 'Basico'),
                        ('advanced', 'Avanzado'),
                        ('premium', 'Premium'),
                        ('elite', 'Elite'),
                        ('esential', 'Esential')
                    ],
                    default='pending',
                    max_length=10,
                    verbose_name='Tipo de plan'
                )),
                ('status_payment_plan', models.BooleanField(default=False, verbose_name='Estado de pago')),
                ('time_quantity_plan', models.PositiveIntegerField(blank=True, default=1, null=True, verbose_name='Cantidad de Tiempo')),
                ('time_unit_plan', models.CharField(
                    choices=[
                        ('day', 'Día(s)'),
                        ('month', 'Mes(es)'),
                        ('year', 'Año(s)')
                    ],
                    blank=True,
                    max_length=50,
                    null=True,
                    verbose_name='Unidad de Tiempo'
                )),
                ('end_date_plan', models.DateField(blank=True, null=True, verbose_name='Fecha de fin')),
                ('total', models.DecimalField(
                    blank=True,
                    decimal_places=2,
                    default=0.0,
                    max_digits=10,
                    null=True,
                    verbose_name='Costo total'
                )),
                ('company', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    to='users.company',
                    verbose_name='Empresa'
                )),
                ('module', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    to='users.module',
                    verbose_name='Módulos'
                )),
            ],
        ),
    ]

