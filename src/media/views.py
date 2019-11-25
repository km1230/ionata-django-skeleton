"""Views for Media."""
from rest_framework_json_api import views

from media.models import Media
from media.serializers import MediaSerializer


class MediaViewSet(views.ModelViewSet):
    """ViewSet for Media."""

    queryset = Media.objects.all()
    serializer_class = MediaSerializer
