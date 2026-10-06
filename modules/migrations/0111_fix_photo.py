from django.db import migrations, models


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
    ]
