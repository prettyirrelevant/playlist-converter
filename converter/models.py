from uuid import uuid4

from django.db import models

from .enums import StreamingPlatform


class Playlist(models.Model):
    uuid = models.UUIDField("uuid", primary_key=True, db_index=True, default=uuid4, editable=False)
    platform = models.CharField("platform", choices=StreamingPlatform.choices, max_length=20)
    metadata = models.JSONField("metadata")
    date_created = models.DateTimeField(auto_now_add=True)

    def __repr__(self) -> str:
        return f"<Playlist uuid={self.uuid.hex} platform={self.platform}>"
