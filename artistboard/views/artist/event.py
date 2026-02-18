from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from iommi import Table, Page, Column, Form, html, Field

from artistboard.models import EventArtist, Season, Artist, Event


class EventArtistsTable(Table):
    delete = Column.delete()

    class Meta:
        auto__model = EventArtist
        auto__include = ["event__show__season", "event__show__name", "event__start_date"]
        rows = lambda pk, **_: EventArtist.objects.filter(artist__pk=pk)
        columns__event_show_season__filter__include = True
        query__form__fields__event_show_season__initial = lambda **_: Season.objects.last()
        title = lambda pk, **kwargs: _("Opportunities for %s") % Artist.objects.get(pk=pk).name


class EventArtistsPage(Page):
    back = html.div(
        children__backlink=html.a(
            _("← Back to artists"),
            attrs__href=lambda **_: reverse("main_menu.artists"),
        )
    )
    back_hr = html.br(attrs__clear="all")
    opportunities = EventArtistsTable()
    new_opportunity = Form.create(
        title=_("New opportunity"),
        auto__model=EventArtist,
        fields__event__choices=lambda pk, **_:
        Event.objects.exclude(pk__in=list(map(
            lambda event_artist: event_artist.event.pk,
            list(EventArtist.objects.filter(artist__pk=pk))
        ))),
        fields__artist=Field.non_rendered(initial=lambda pk, **_: Artist.objects.get(pk=pk)),
        extra__redirect_to=".",
    )


event_artists_delete = Form.delete(instance=lambda pk, **_: EventArtist.objects.get(pk=pk))
