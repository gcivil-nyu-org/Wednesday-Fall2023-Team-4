# Generated by Django 4.2 on 2023-12-07 01:34

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rrapp", "0019_alter_user_rating"),
    ]

    operations = [
        migrations.AddField(
            model_name="listing",
            name="lease_status",
            field=models.CharField(
                choices=[("new", "New"), ("existing", "Existing")],
                default="new",
                max_length=20,
            ),
        ),
    ]
