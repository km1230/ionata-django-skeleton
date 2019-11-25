"""Application for media."""
from django.apps import AppConfig


class MediaConfig(AppConfig):
    """Core class for application configuration."""

    name = "media"

    def ready(self):
        """Import signals when the stack has started up."""
        from media import signals  # noqa pylint: disable=unused-import
