# Generated by Django 5.0.6 on 2024-07-24 00:07

import pgvector.django
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="MentorshipDocuments",
            fields=[
                ("id", models.UUIDField(primary_key=True, serialize=False)),
                ("content", models.TextField(blank=True, null=True)),
                ("metadata", models.JSONField(blank=True, null=True)),
                (
                    "embedding",
                    pgvector.django.VectorField(blank=True, dimensions=1536, null=True),
                ),
            ],
            options={
                "db_table": "mentorship_documents",
                "managed": False,
            },
        ),
    ]
