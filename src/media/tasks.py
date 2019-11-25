"""Tasks related to media."""
from io import BytesIO
from mimetypes import guess_type

from celery import shared_task
from django.core.files.base import ContentFile
from PIL import Image, ImageOps

from media.models import IMAGE_RESOLUTIONS, Media, Rendition


@shared_task
def make_renditions(media_id: int):
    """Create the smaller versions of all provided files."""
    original = Media.objects.filter(pk=media_id).first()
    if original is None:
        return
    mime, _ = guess_type(original.media.name)
    if mime is None or "image/" not in mime:
        return
    image_format = mime.split("/")[-1]
    name = original.name
    renditions = {r.resolution: r for r in original.renditions.all()}
    for name, (max_x, max_y) in IMAGE_RESOLUTIONS.items():
        if name in renditions:
            continue
        image = Image.open(original.media)
        width, height = image.size
        cropped: Image
        if 0 in [max_x, max_y]:
            cropped = image.copy()
            cropped.thumbnail((max_x or width, max_y or height), Image.LANCZOS)
        else:
            cropped = ImageOps.fit(image, (max_x, max_y), Image.LANCZOS)
        media = BytesIO()
        cropped.save(media, format=image_format)
        rendition = Rendition.objects.create(original=original, resolution=name)
        rendition.media.save(f"{name}__{original.name}", ContentFile(media.getvalue()))
        rendition.save()
        renditions[name] = rendition
