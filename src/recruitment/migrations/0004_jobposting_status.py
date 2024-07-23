# Generated by Django 5.0.6 on 2024-07-19 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recruitment", "0003_remove_essayanswer_unique_applicant_application"),
    ]

    operations = [
        migrations.AddField(
            model_name="jobposting",
            name="status",
            field=models.CharField(
                choices=[
                    ("pre_open", "Pre_Open"),
                    ("open", "Open"),
                    ("closed", "Closed"),
                ],
                default="pre_open",
                max_length=10,
            ),
        ),
    ]
