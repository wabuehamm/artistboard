from django.urls import reverse
from iommi import Column, EditColumn, EditTable, Field, Form, Page, Table

from ..models import Artist, Event, EventArtist, EventTodo
from iommi.form import save_nested_forms


class EventView(Page):
    events = Table(
        auto__model=Event,
        page_size=20,
        columns__agreement__include=False,
        columns__required_free_tickets__include=False,
        columns__required_paid_tickets__include=False,
        columns__season=Column(
            attr="show__season__year",
            filter__include=True,
        ),
        columns__artists=Column(
            cell__value=lambda row, **_: EventArtist.objects.filter(event=row)
        ),
        columns__show__filter__include=True,
        columns__edit=Column.edit(),
        columns__delete=Column.delete(),
    )
    new_event = Form.create(
        title="New Event",
        auto__model=Event,
        fields__booked_artist__include=False,
        fields__agreement__include=False,
        fields__required_free_tickets__include=False,
        fields__required_paid_tickets__include=False,
        extra__redirect_to=".",
    )


def fetch_artists(event_pk):
    artists = []
    for ref in EventArtist.objects.filter(event=event_pk):
        artists.append(ref.artist.pk)
    return Artist.objects.filter(pk__in=artists)


class EventEdit(Form):
    event = Form.edit(
        auto__model=Event,
        instance=lambda pk, **_: Event.objects.get(pk=pk),
        fields__booked_artist__choices=lambda pk, **_: fetch_artists(pk),
    )
    todos = EditTable(
        auto__model=EventTodo,
        columns__event__include=False,
        columns__description=Column(attr="todo__description", after=3),
        columns__done__field__include=True,
        rows=lambda pk, **_: EventTodo.objects.filter(event__pk=pk),
        edit_actions__add_row__include=False,
    )
    interested_artists = EditTable(
        auto__model=EventArtist,
        rows=lambda pk, **_: EventArtist.objects.filter(event=pk),
        columns__event__field=Field.non_rendered(
            initial=lambda pk, **_: Event.objects.get(pk=pk)
        ),
        columns__delete=EditColumn.delete(),
        **{
            "attrs__data-iommi-edit-table-delete-with": "checkbox",
        }
    )

    class Meta:
        actions__submit__post_handler = save_nested_forms
        extra__redirect_to = lambda **_: reverse("main_menu.events")


event_delete = Form.delete(instance=lambda pk, **_: Event.objects.get(pk=pk))
