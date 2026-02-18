from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from iommi import Column, Page, Table, html

from artistboard.models import Event, Artist


class BookingOverviewTable(Table):
    event = Column(
        display_name=_("Event"),
        cell__value=lambda row, **_: row,
        cell__url=lambda row, **_: reverse("event-edit", kwargs={"pk": row.pk})
    )

    booking_artists = Column(display_name=_("Opportunities"),
                             cell__value=lambda row, **_: mark_safe(row.booking_artists()))
    booking_least_events = Column(render_column=False, cell__value=lambda row, **_: row.booking_least_events)

    class Meta:
        title = _("Booking overview")
        rows = lambda season_pk, **_: list(
            Event.objects.filter(show__season__pk=season_pk, booked_artist=None)
        )
        default_sort_order = "booking_least_events"


class UnbookedArtistsTable(Table):
    events = Column(
        display_name=_("Events"),
        cell__value=lambda row, **_: mark_safe(row.event_links())
    )

    class Meta:
        title = _("Unbooked artists")
        auto__model = Artist
        auto__include = ["name", "contact_name", "style", "number_artists", "rating"]
        rows = lambda season_pk, **_: filter(
            lambda artist: Event.objects.filter(
                show__season__pk=season_pk,
                booked_artist=artist
            ).count() == 0,
            Artist.objects.filter(locked=False)
        )
        columns__name__cell__url = lambda row, **_: reverse("artist-edit", kwargs={"pk": row.pk})


class BookingOverviewPage(Page):
    back = html.div(
        children__backlink=html.a(
            _("← Back to seasons"),
            attrs__href=lambda **_: reverse("main_menu.seasons"),
        )
    )
    back_hr = html.br(attrs__clear="all")
    events = BookingOverviewTable()
    unbooked_artists = UnbookedArtistsTable()
