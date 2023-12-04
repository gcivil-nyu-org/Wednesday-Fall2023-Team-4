# Generated by Django 4.2 on 2023-12-03 21:01

from django.db import migrations, models
import rrapp.models


class Migration(migrations.Migration):
    dependencies = [
        ("rrapp", "0013_rating_created_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="listing",
            name="restrict_to_matches",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="quiz",
            name="question2",
            field=models.IntegerField(
                choices=[
                    (
                        1,
                        "Wait for that paycheck – you'll justhave to spend as little as possible until then.",
                    ),
                    (
                        2,
                        "Ask your roommate for a small loan and payhim/her back when you get your paycheck.",
                    ),
                    (
                        3,
                        "Ask your roommate for a small loan,and pay him/her back in installments.",
                    ),
                    (
                        4,
                        "Take some money out of your roommate'stop drawer and return it as soon as you get your pay.",
                    ),
                ],
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="profile_picture",
            field=models.ImageField(
                default="/home/himanshu/linuxWorkspace/fall23_gcivil/temp/Wednesday-Fall2023-Team-4/media/DefaultProfile.jpg",
                upload_to=rrapp.models.user_directory_path,
            ),
        ),
    ]