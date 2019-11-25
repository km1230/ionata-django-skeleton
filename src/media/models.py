"""Models for media."""
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.db import models

from media.utils import UniqueFileName


class Media(models.Model):
    """Model for file uploads."""

    creator = models.ForeignKey(to=get_user_model(), on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)

    media = models.FileField(upload_to=UniqueFileName())
    name = models.TextField(default="", blank=True)
    metadata = JSONField(default=dict, blank=True)

    class JSONAPIMeta:
        """JSONAPI meta information."""

        resource_name = "media"

    @property
    def image(self) -> str:
        """Return the URI for accessing the file."""
        try:
            return self.media.url
        except ValueError:
            return ""

    @property
    def thumbnail(self) -> str:
        """Show the thumbnail for the media file, falling back to the original."""
        img = [x for x in self.renditions.all() if x.resolution == "thumbnail"]
        return img[0].image if img else self.image


# name, (width, height)  # 0 for unlimited
IMAGE_RESOLUTIONS = {
    "large": (1024, 0),
    "medium": (768, 0),
    "small": (280, 0),
    "thumbnail": (200, 200),
}
IMAGE_RESOLUTIONS_CHOICES = [(k, k) for k in IMAGE_RESOLUTIONS]


class Rendition(models.Model):
    """Resizing of media."""

    created = models.DateTimeField(auto_now_add=True)

    original = models.ForeignKey(
        to=Media, on_delete=models.CASCADE, related_name="renditions"
    )
    resolution = models.CharField(max_length=255, choices=IMAGE_RESOLUTIONS_CHOICES)
    media = models.FileField(upload_to=UniqueFileName())

    class Meta:
        """Model meta options."""

        unique_together = [("original", "resolution")]

    class JSONAPIMeta:
        """JSONAPI meta information."""

        resource_name = "renditions"

    @property
    def image(self) -> str:
        """Return the URI for accessing the file."""
        try:
            return self.media.url
        except ValueError:
            return ""
