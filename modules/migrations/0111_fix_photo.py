from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ("modules", "0110_fix_evidence_images"),
    ]

    operations = [
        migrations.AddField(
            model_name="equipments_tools_detail",
            name="photo",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to="docs/",
            ),
        ),

        migrations.AddField(
            model_name='infrastructure_maintenance',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='infrastructureitemdetail',
            name='deactivated_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Fecha de baja del activo'),
        ),
        migrations.AddField(
            model_name='infrastructureitemdetail',
            name='deactivation_description',
            field=models.TextField(blank=True, null=True, verbose_name='Descripción de la baja del activo'),
        ),
        migrations.AddField(
            model_name='infrastructureitemdetail',
            name='deactivation_reason',
            field=models.CharField(blank=True, choices=[('VENDIDO', 'Vendido'), ('OBSOLETO', 'Obsoleto'), ('PERDIDO', 'Perdido'), ('BAJA', 'Baja'), ('ROBADO', 'Robado')], max_length=20, null=True, verbose_name='Motivo de baja del activo'),
        ),
        migrations.AddField(
            model_name='infrastructureitemdetail',
            name='evidence1_image',
            field=models.FileField(blank=True, null=True, upload_to='docs/'),
        ),
        migrations.AddField(
            model_name='infrastructureitemdetail',
            name='evidence2_image',
            field=models.FileField(blank=True, null=True, upload_to='docs/'),
        ),

        
        migrations.AddField(
            model_name='infrastructureitemdetail',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='infrastructureitemdetail',
            name='is_deactivated',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='infrastructureitemdetail',
            name='photo_infraestructure',
            field=models.FileField(blank=True, null=True, upload_to='docs/', verbose_name='Imagen del registro'),
        ),
        migrations.RemoveField(
            model_name='infrastructureitemdetail',
            name='qr_info_infrastructure',
        ),
        migrations.AddField(
            model_name='infrastructureitemdetail',
            name='user_modification',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='infrastructure_details_modified', to=settings.AUTH_USER_MODEL, verbose_name='Usuario que realizó la modificación'),
        ),
        migrations.AlterField(
            model_name='infrastructureitemdetail',
            name='responsible',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='infrastructure_details_responsible', to=settings.AUTH_USER_MODEL, verbose_name='Responsable temporal'),
        ),
    ]
