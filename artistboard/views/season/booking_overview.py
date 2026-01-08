from django.urls import reverse
from iommi import Column, Page, Table, html
from artistboard.models import Event, EventArtist


class BookingOverviewTable(Table):
    show = Column(cell__value=lambda row, **_: row.show)
    start_date = Column(cell__value=lambda row, **_: row.start_date)
    start_time = Column(cell__value=lambda row, **_: row.start_time)

    booking_artists = Column(cell__value=lambda row, **_: row.booking_artists)
    booking_least_events = Column(cell__value=lambda row, **_: row.booking_least_events)

    class Meta:
        title = "Booking overview"
        rows = lambda season_pk, **_: list(
            Event.objects.filter(show__season__pk=season_pk, booked_artist=None)
        )
        default_sort_order = "booking_least_events"


class BookingOverviewPage(Page):
    back = html.div(
        children__backlink=html.a(
            "← Back to seasons",
            attrs__href=lambda **_: reverse("main_menu.seasons"),
        )
    )
    back_hr = html.br(attrs__clear="all")
    events = BookingOverviewTable()
