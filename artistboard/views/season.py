from django.http import HttpResponseRedirect
from django.urls import reverse
from iommi import Action, Column, EditColumn, EditTable, Field, Form, Page, Table

from ..models import MailTemplate, Season, SeasonTodo, Show
from iommi.form import save_nested_forms
from datetime import datetime
from django.contrib.auth.decorators import login_required


from django.utils.decorators import method_decorator


class SeasonView(Page):
    seasons = Table(
        auto__model=Season,
        page_size=10,
        columns__shows=Column(
            cell__value=lambda row, **_: Show.objects.filter(season=row)
        ),
        columns__events=Column.link(
            attr=None,
            cell__url=lambda row, **_: reverse(
                "main_menu.events", query={"season": row.year}
            ),
            cell__value="Events",
        ),
        columns__edit=Column.edit(),
        columns__delete=Column.delete(),
    )
    new_season = Form.create(
        title="New season",
        auto__model=Season,
        extra__redirect_to=".",
        fields__year__initial=lambda **_: datetime.now().year + 1,
    )


class SeasonEditForm(Form):
    season = Form.edit(
        auto__model=Season, instance=lambda pk, **_: Season.objects.get(pk=pk)
    )
    todos = EditTable(
        auto__model=SeasonTodo,
        columns__season__include=False,
        columns__description=Column(attr="todo__description", after=3),
        columns__done__field__include=True,
        rows=lambda pk, **_: SeasonTodo.objects.filter(season__pk=pk),
        edit_actions__add_row__include=False,
    )
    shows = EditTable(
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


def handle_send_mail(form, **_):
    if form.is_valid():
        return HttpResponseRedirect(
            reverse(
                "mail-preview",
                query=dict(
                    object=form.fields["season"].value,
                    template=form.fields["template"].value.pk,
                ),
            )
        )


class SeasonEdit(Page):
    edit = SeasonEditForm()

    send_mail = Form(
        title="Send mail",
        fields__template=Field.choice_queryset(
            choices=MailTemplate.objects.filter(type="single_season")
        ),
        fields__season=Field.hidden(initial=lambda pk, **_: pk),
        actions__preview=Action.primary(
            display_name="Preview", post_handler=handle_send_mail
        ),
    )


season_delete = Form.delete(instance=lambda pk, **_: Season.objects.get(pk=pk))
