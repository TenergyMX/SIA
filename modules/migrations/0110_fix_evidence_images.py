from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("modules", "0109_detail_responsiva_vehicles_responsivas_pdf_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="equipments_tools_detail",
            name="evidence1_image",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to="docs/",
            ),
        ),
        migrations.AddField(
            model_name="equipments_tools_detail",
            name="evidence2_image",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to="docs/",
            ),
        ),
    ]
