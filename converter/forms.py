from django import forms
from django.utils.translation import gettext_lazy as _

from .enums import StreamingPlatform


class PlaylistConverterForm(forms.Form):
    title = forms.CharField(
        label=_("Title"),
        max_length=70,
        help_text=_("A name to call the new playlist."),
    )
    playlist_id = forms.CharField(
        label=_("Playlist ID"),
        max_length=100,
        help_text=_("The ID of the Playlist to convert."),
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
        cleaned_data = super().clean()
        source = cleaned_data.get("source")
        target = cleaned_data.get("target")

        if source == target:
            self.add_error("source", " ")
            self.add_error("target", "Source and target cannot be the same platform.")
