# Generated by Django 4.2 on 2023-11-11 21:26

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("chat", "0004_alter_directmessagepermission_options_and_more"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Message",
        ),
        migrations.AlterUniqueTogether(
            name="directmessagepermission",
            unique_together={("sender", "receiver")},
        ),
    ]