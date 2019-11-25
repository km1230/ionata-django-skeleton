"""Serializers for Media."""
from rest_framework_json_api import serializers

from media.models import Media, Rendition
from users.serializers import UserSerializer


class RenditionSerializer(serializers.ModelSerializer):
    """Serializer for renditions."""

    class Meta:
        """Class meta options for Renditions."""

        model = Rendition
        read_only_fields = ["id", "resolution", "media", "image"]
        fields = read_only_fields


class MediaSerializer(serializers.ModelSerializer):
    """Serializer for renditions."""

    included_serializers = {
        "creator": UserSerializer,
        "renditions": RenditionSerializer,
    }

    class Meta:
        """Class meta options for Media."""

        model = Media
        included_resources = ["creator", "site"]
        read_only_fields = [
            "id",
            "created",
            "creator",
            "image",
            "renditions",
            "thumbnail",
        ]
        fields = read_only_fields + ["name", "metadata", "media"]

    def validate(self, attrs):
        """Add the request user."""
        if "request" in self._context:
            attrs["creator"] = self.context["request"].user
        return attrs
