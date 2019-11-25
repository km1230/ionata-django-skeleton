"""Signals handled by the media app."""
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from media.models import Media
from media.tasks import make_renditions


# pylint: disable=unused-argument
@receiver(post_save, sender=Media)
def add_renditions(sender, instance, raw=False, created=False, **kwargs):
    """Ensure we create smaller versions of every image uploaded."""
    if raw:
        return
    make_renditions.delay(instance.pk)
