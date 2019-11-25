from typing import List, Tuple

from rest_framework.viewsets import ViewSetMixin  # type: ignore

from media import views as media_views

# Add viewsets from apps in the format "routes = [(r'regex', MyViewSet), ...]"
routes: List[Tuple[str, ViewSetMixin]] = [
    ("media", media_views.MediaViewSet),
]
