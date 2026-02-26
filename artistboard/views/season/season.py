from datetime import datetime

from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from iommi import Column, EditColumn, EditTable, Field, Form, Page, Table
from iommi.form import save_nested_forms

from artistboard.models import Season, SeasonTodo, Show
from artistboard.views.mail_template import SendMailForm


def season_todos(pk):
    return ", ".join(map(
        lambda todo: '<a href="%s">%s</a>' % (
            reverse("season-todo-toggle", kwargs={"pk": pk, "todo_pk": todo.pk}),
            todo.__str__(),
        ),
        SeasonTodo.objects.filter(season__pk=pk)
    ))


class SeasonView(Page):
    seasons = Table(
        title=_("Seasons"),
        auto__model=Season,
        page_size=10,
        columns__shows=Column(
            cell__value=lambda row, **_: Show.objects.filter(season=row)
        ),
        columns__events=Column.link(
            display_name=_("Events"),
            attr=None,
            cell__url=lambda row, **_: reverse(
                "main_menu.events", query={"season": row.pk}
            ),
            cell__value=_("Events"),
        ),
        columns__overview=Column.link(
            display_name=_("Booking overview"),
            attr=None,
            cell__url=lambda row, **_: reverse(
                "booking-overview", kwargs={"season_pk": row.pk}
            ),
            cell__value=_("Booking overview"),
        ),
        columns__todos=Column(
            display_name=_("Season todos"),
            cell__value=lambda row, **_: mark_safe(season_todos(row.pk)),
        ),
        columns__edit=Column.edit(),
        columns__delete=Column.delete(),
    )
    new_season = Form.create(
        title=_("New season"),
        auto__model=Season,
        extra__redirect_to=".",
        fields__year__initial=lambda **_: datetime.now().year + 1,
    )


class SeasonEditForm(Form):
    season = Form.edit(
        title=_("Season"),
        auto__model=Season, instance=lambda pk, **_: Season.objects.get(pk=pk)
    )
    todos = EditTable(
        title=_("Todos"),
        auto__model=SeasonTodo,
        columns__season__include=False,
        columns__description=Column(attr="todo__description", after=3),
        columns__done__field__include=True,
        rows=lambda pk, **_: SeasonTodo.objects.filter(season__pk=pk),
        edit_actions__add_row__include=False,
    )
    shows = EditTable(
        title=_("Shows"),
        auto__model=Show,
        rows=lambda pk, **_: Show.objects.filter(season__pk=pk),
        columns__season__field=Field.non_rendered(
            initial=lambda pk, **_: Season.objects.get(pk=pk)
        ),
        columns__name__field__include=True,
        columns__delete=EditColumn.delete(),
        **{
            "attrs__data-iommi-edit-table-delete-with": "checkbox",
        }
    )

    class Meta:
        actions__submit__post_handler = save_nested_forms
        extra__redirect_to = lambda **_: "/seasons"


class SeasonSendMailForm(SendMailForm):
    object = Field.hidden(initial=lambda pk, **_: pk)

    class Meta:
        extra__template_type = "single_season"


class SeasonEdit(Page):
    edit = SeasonEditForm()

    send_mail = SeasonSendMailForm()


season_delete = Form.delete(instance=lambda pk, **_: Season.objects.get(pk=pk))
