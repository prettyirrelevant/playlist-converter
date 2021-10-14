from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.views import generic

from .forms import PlaylistConverterForm, StreamingPlatform
from .models import Playlist
from .services import spotify, ytmusic


class IndexView(generic.ListView):
    template_name = "index.html"
    model = Playlist
    context_object_name = "playlists"
    paginate_by = 4

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Home | PlaylistConverter"

        return context


class ConvertPlaylistView(generic.FormView):
    form_class = PlaylistConverterForm
    template_name = "convert.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Convert | Playlist Converter"
        return context

    def form_valid(self, form):
        source, target = form.cleaned_data.get("source"), form.cleaned_data.get("target")
        if source == StreamingPlatform.SPOTIFY and target == StreamingPlatform.YOUTUBE:
            try:
                playlist = ytmusic.from_spotify(
                    form.cleaned_data.get("playlist_id"),
                    form.cleaned_data.get("title"),
                )
                playlist = Playlist.objects.create(
                    metadata=playlist, platform=StreamingPlatform.YOUTUBE
                )
                messages.success(self.request, "Playlist created successfully!")
                return redirect(reverse("view-playlist", kwargs={"uuid": playlist.uuid.hex}))
            except Exception as err:
                messages.error(self.request, str(err))
                return redirect(reverse("index"))

        elif source == StreamingPlatform.YOUTUBE and target == StreamingPlatform.SPOTIFY:
            self.request.session["playlist_id"] = form.cleaned_data.get("playlist_id")
            self.request.session["title"] = form.cleaned_data.get("title")

            return redirect(spotify.get_authorize_url())


class PlaylistView(generic.DetailView):
    template_name = "playlist.html"
    model = Playlist
    context_object_name = "playlist"
    pk_url_kwarg = "uuid"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Playlist {self.get_object().uuid.hex} | PlaylistConverter"

        return context


class SpotifyCallbackView(generic.View):
    def get(self, *args, **kwargs):
        code = self.request.GET.get("code")
        if not code:
            return redirect(reverse("index"))

        spotify.get_access_token(code)

        if self.request.session["playlist_id"] and self.request.session["title"]:
            try:
                playlist = spotify.from_ytmusic(
                    self.request.session.pop("playlist_id", None),
                    self.request.session.pop("title", None),
                )
                playlist = Playlist.objects.create(
                    metadata=playlist, platform=StreamingPlatform.SPOTIFY
                )
                messages.success(self.request, "Playlist created successfully!")
                return redirect(reverse("view-playlist", kwargs={"uuid": playlist.uuid.hex}))
            except Exception as err:
                messages.error(self.request, str(err))
                return redirect(reverse("index"))
