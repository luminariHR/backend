# Generated by Django 4.2 on 2024-07-10 15:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("chatbot", "0002_chatbotdocument_delete_document"),
    ]

    operations = [
        migrations.DeleteModel(
            name="ChatbotDocument",
        ),
        migrations.AlterField(
            model_name="message",
            name="post",
            field=models.ForeignKey(
                default="",
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
