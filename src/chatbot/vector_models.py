from django.db import models
from pgvector.django import VectorField


class Documents(models.Model):
    id = models.UUIDField(primary_key=True)
    content = models.TextField(blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)
    embedding = VectorField(dimensions=1536, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "documents"
