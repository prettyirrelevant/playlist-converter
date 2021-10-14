from django import template

register = template.Library()


@register.filter
def join_artists(artists: list) -> str:
    return ", ".join([artist["name"] for artist in artists])
