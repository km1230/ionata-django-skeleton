"""Tests for media."""
from __future__ import annotations

from io import BytesIO
from typing import Dict

from django.core.files.uploadedfile import InMemoryUploadedFile
from hamcrest import instance_of
from PIL import Image

from media.models import IMAGE_RESOLUTIONS, Media
from users.models import User
from webapp.tests.base import JsonApiTestCase
from webapp.tests.matchers import (
    IsJsonApiRelationship,
    is_date,
    is_to_many,
    is_to_one,
    is_url,
)


def get_image() -> BytesIO:
    """Create a dummy image."""
    fyle = BytesIO(b"")
    Image.new("RGB", (1920, 1080)).save(fyle, format="jpeg")
    fyle.seek(0)
    fyle.name = "image.jpg"
    return fyle


class MediaTestCase(JsonApiTestCase):
    """Tests for the media model."""

    resource_name: str = "media"
    attributes = {
        "created": is_date(),
        "name": instance_of(str),
        "media": is_url(),
        "image": is_url(),
        "thumbnail": is_url(),
        "metadata": instance_of(dict),
    }
    relationships: Dict[str, IsJsonApiRelationship] = {
        "creator": is_to_one(resource_name="users"),
        "renditions": is_to_many(resource_name="renditions", optional=True),
    }

    user1: User
    user2: User
    staff: User

    @classmethod
    def setUpClass(cls):
        """Set up necessary data for tests."""
        super().setUpClass()
        _fn = User.objects.create_user
        cls.user1 = _fn(email="user1@example.com", password="passWORD9")
        cls.user2 = _fn(email="user2@example.com", password="passWORD9")
        cls.staff = _fn(email="staff@example.com", password="passWORD9")
        cls.give_user_perm(cls.staff, "media.add_media")

    def test_staff_create(self):
        """Test a staff member can create an image."""
        self.auth(self.staff)
        data = {"media": get_image(), "name": "testing"}
        json = self.post(
            f"/{self.resource_name}/",
            data,
            format="multipart",
            asserted_status=201,
            asserted_schema=self.get_schema(),
        ).json()["data"]
        attrs = json["attributes"]
        rels = json["relationships"]
        cnt = len(IMAGE_RESOLUTIONS)
        self.assertEqual(cnt, int(rels["renditions"]["meta"]["count"]))
        self.assertEqual(str(self.staff.pk), rels["creator"]["data"]["id"])
        self.assertEqual(data["name"], attrs["name"])

    def test_anon_get(self):
        """Test anon users can retrieve the media list."""
        json = self.get(
            f"/{self.resource_name}/",
            asserted_status=200,
            asserted_schema=self.get_schema(many=True),
        ).json()
        self.assertEqual(0, len(json["data"]))
        raw = get_image()
        mem = InMemoryUploadedFile(
            raw, None, 'foo.jpg', 'image/jpeg', raw.tell, None)
        img = Media.objects.create(
            name="testing", creator=self.staff, media=mem
        )
        json = self.get(
            f"/{self.resource_name}/",
            asserted_status=200,
            asserted_schema=self.get_schema(many=True),
        ).json()
        self.assertEqual(1, len(json["data"]))
        self.assertEqual(img.pk, int(json["data"][0]["id"]))
        attrs = json["data"][0]["attributes"]
        rels = json["data"][0]["relationships"]
        self.assertEqual(img.name, attrs["name"])
        cnt = len(IMAGE_RESOLUTIONS)
        self.assertEqual(cnt, int(rels["renditions"]["meta"]["count"]))
        self.assertEqual(str(self.staff.pk), rels["creator"]["data"]["id"])
