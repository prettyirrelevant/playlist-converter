from django.urls import include, path

urlpatterns = [
    path("", include("converter.urls")),
]
