from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Department


@receiver(post_save, sender=Department)
def ensure_head_is_member(sender, instance, **kwargs):
    if instance.head and instance.head.department != instance:
        instance.head.department = instance
        instance.head.save()
