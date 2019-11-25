"""Utilities surrounding media."""
import os
from typing import Dict
from uuid import uuid4

from django.db import models
from django.utils.deconstruct import deconstructible
from django.utils.http import int_to_base36


@deconstructible
class UniqueFileName:
    """Provide a path, a random datestamped filename will be returned."""

    def __init__(self, path="{app_label}/{model_name}", extension=""):
        """Store the arguments."""
        super().__init__()
        self.path = path
        self.extension = extension

    @staticmethod
    def get_path_options(instance: models.Model) -> Dict[str, str]:
        """Add the potential template items for a path."""
        labels = [
            "app_label",
            "default_manager_name",
            "label",
            "label_lower",
            "model_name",
            "object_name",
            "verbose_name",
            "verbose_name_plural",
            "verbose_name_raw",
        ]
        return {label: getattr(instance._meta, label, "") for label in labels}

    def __call__(self, instance: models.Model, filename: str) -> str:
        """Generate the name of the file."""
        if "." not in filename and self.extension != "":
            filename = f"{filename}.{self.extension}"
        filename = f"{int_to_base36(uuid4().int)}__{filename}"
        new_path = self.path.format(**self.get_path_options(instance))
        return os.path.join(new_path, filename)
