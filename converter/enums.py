from django.db.models import TextChoices


class PlaylistType(TextChoices):
    YOUTUBE = "YOUTUBE"
    SPOTIFY = "SPOTIFY"

class StreamingPlatform(TextChoices):
    SPOTIFY = "SPOTIFY"
    YOUTUBE = "YOUTUBE"
