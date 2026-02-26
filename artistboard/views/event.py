from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from iommi import Column, EditColumn, EditTable, Field, Form, Page, Table
from iommi.form import save_nested_forms

from .mail_template import SendMailForm
from ..models import Artist, Event, EventArtist, EventTodo, Season


def event_todos(pk):
    return ", ".join(map(
        lambda todo: '<a href="%s">%s</a>' % (
            reverse("event-todo-toggle", kwargs={"pk": pk, "todo_pk": todo.pk}),
            todo.__str__(),
        ),
        EventTodo.objects.filter(event__pk=pk)
    ))


class EventView(Page):
    events = Table(
        title=_("Events"),
        auto__model=Event,
        page_size=20,
        columns__agreement__include=False,
        columns__required_free_tickets__include=False,
        columns__required_paid_tickets__include=False,
        columns__season=Column.choice_queryset(
            display_name=_("Season"),
            attr="show__season",
            model=Season,
            choices=Season.objects.all(),
            filter__include=True,
            filter__field__search_fields=["year"],

        ),
        query__form__fields__season__initial=lambda request, **_: Season.objects.get(
            pk=request.GET["season"]
        ) if "season" in request.GET else None,
        columns__artists=Column(
            display_name=_("Artists"),
            cell__value=lambda row, **_: mark_safe(row.booking_artists())
        ),
        columns__todos=Column(
            display_name=_("Event todos"),
            cell__value=lambda row, **_: mark_safe(event_todos(row.pk)),
        ),
        columns__booked_artist__cell__url=lambda row, **_: reverse(
            "artist-edit",
            kwargs={
                'pk': row.booked_artist.pk
            }
        ) if row.booked_artist is not None else "",
        columns__show__filter__include=True,
        columns__booked_artist__filter__include=True,
        columns__edit=Column.edit(),
        columns__delete=Column.delete(),
    )
    new_event = Form.create(
        title=_("New event"),
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


def get_booked_artist_initial(instance, **kwargs):
    if instance.booked_artist is not None:
        return instance.booked_artist
    elif "artist_pk" in kwargs:
        return Artist.objects.get(pk=kwargs["artist_pk"])
    return None


class EventEditForm(Form):
    event = Form.edit(
        title=_("Event"),
        auto__model=Event,
        instance=lambda pk, **_: Event.objects.get(pk=pk),
        fields__booked_artist__choices=lambda pk, **_: fetch_artists(pk),
        fields__booked_artist__initial=lambda pk, instance, **kwargs: get_booked_artist_initial(instance, **kwargs),
    )
    todos = EditTable(
        title=_("Todos"),
        auto__model=EventTodo,
        columns__event__include=False,
        columns__description=Column(attr="todo__description", after=3),
        columns__done__field__include=True,
        rows=lambda pk, **_: EventTodo.objects.filter(event__pk=pk),
        edit_actions__add_row__include=False,
    )
    opportunities = EditTable(
        title=_("Opportunities"),
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


class EventSendMailForm(SendMailForm):
    object = Field.hidden(initial=lambda pk, **_: pk)

    class Meta:
        extra__template_type = "single_event"


class EventEdit(Page):
    edit_event = EventEditForm()

    send_mail = EventSendMailForm()


event_delete = Form.delete(instance=lambda pk, **_: Event.objects.get(pk=pk))
