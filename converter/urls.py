from django.urls import path

from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("convert", views.ConvertPlaylistView.as_view(), name="convert"),
    path("playlists/<uuid>", views.PlaylistView.as_view(), name="view-playlist"),
    path("spotify/callback", views.SpotifyCallbackView.as_view(), name="callback"),
]
