from urllib.parse import urlparse

from django import forms
from django.utils.translation import gettext_lazy as _

from .enums import StreamingPlatform


class PlaylistConverterForm(forms.Form):
    title = forms.CharField(
        label=_("Title"),
        max_length=70,
        help_text=_("A name to call the new playlist."),
    )
    playlist_link = forms.URLField(
        label=_("Playlist Link"),
        max_length=100,
        help_text=_("The link of the playlist to convert."),
    )
    source = forms.ChoiceField(
        label=_("Source"),
        help_text=_("The platform the playlist to be converted comes from."),
        choices=StreamingPlatform.choices,
    )
    target = forms.ChoiceField(
        label=_("Target"),
        help_text=_("The platform where the playlist should be replicated."),
        choices=StreamingPlatform.choices,
    )

    def clean(self):
        accepted_domains = ["open.spotify.com", "music.youtube.com", "youtube.com"]
        cleaned_data = super().clean()

        source = cleaned_data.get("source")
        target = cleaned_data.get("target")

        playlist_link = cleaned_data.pop("playlist_link")
        playlist_netloc = urlparse(playlist_link).netloc
        
        if playlist_netloc not in accepted_domains:
            self.add_error(
                "playlist_link", f"We currently do not support {playlist_netloc}."
            )

        if source == target:
            self.add_error("source", " ")
            self.add_error("target", "Source and target cannot be the same platform.")

        if playlist_netloc in accepted_domains[1:]:
            cleaned_data.update(
                {"playlist_id": urlparse(playlist_link).query.split("=")[-1]}
            )
        else:
            cleaned_data.update(
                {"playlist_id": urlparse(playlist_link).path.split("/")[-1]}
            )

        return cleaned_data
