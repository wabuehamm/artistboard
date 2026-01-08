from django.urls import reverse
from iommi import Column, Page, Table, html
from artistboard.models import Event, EventArtist


def get_artists(row, **_):
    artists = EventArtist.objects.filter(event=row)
    artist_count = []
    for artist in artists:
        if Event.objects.filter(booked_artist=artist.artist).count() > 0:
            continue
        artist_count.append(
            {
                "name": artist.artist.name,
                "count": EventArtist.objects.filter(
                    artist=artist.artist, event__booked_artist=None
                ).count(),
            }
        )
    artist_count = sorted(artist_count, key=lambda artist: artist["count"])
    return_value = map(
        lambda artist: "%s (%s)" % (artist["name"], artist["count"]), artist_count
    )
    return ",".join(return_value)


class BookingOverviewTable(Table):
    show = Column(cell__value=lambda row, **_: row.show)
    start_date = Column(cell__value=lambda row, **_: row.start_date)
    start_time = Column(cell__value=lambda row, **_: row.start_time)

    artists = Column(cell__value=get_artists)

    class Meta:
        title = "Booking overview"
        rows = lambda season_pk, **_: Event.objects.filter(
            show__season__pk=season_pk, booked_artist=None
        )


class BookingOverviewPage(Page):
    back = html.div(
        children__backlink=html.a(
            "← Back to seasons",
            attrs__href=lambda **_: reverse("main_menu.seasons"),
        )
    )
    back_hr = html.br(attrs__clear="all")
    events = BookingOverviewTable()
