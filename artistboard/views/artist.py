from django.http import HttpResponseRedirect
from django.urls import reverse
from iommi import Action, Column, EditColumn, EditTable, Field, Form, Page, Table

from ..models import Artist, MailTemplate, Link
from iommi.form import save_nested_forms
from django.utils.safestring import mark_safe


def handle_send_mail(form, **_):
    if form.is_valid():
        if form.fields["artist"]:
            return HttpResponseRedirect(
                reverse(
                    "mail-preview",
                    query=dict(
                        object=form.fields["artist"].value,
                        template=form.fields["template"].value.pk,
                    ),
                )
            )
    else:
        return HttpResponseRedirect(
            reverse(
                "mail-preview",
                query=dict(
                    template=form.fields["template"].value.pk,
                ),
            )
        )


class ArtistView(Page):
    artists = Table(
        auto__model=Artist,
        page_size=10,
        columns__name__filter__include=True,
        columns__locked__filter__include=True,
        columns__contact_name__filter__include=True,
        columns__style__filter__include=True,
        columns__rating__filter__include=True,
        columns__image=Column(
            cell__value=lambda row, **_: row.image.url if row.image else "",
            cell__format=lambda value, **_: (
                mark_safe('<img src="%s" />' % (value)) if value != "" else ""
            ),
            cell__attrs__style={"max-width": "4em", "max-height": "4em"},
        ),
        query__form__fields__locked__initial=False,
        columns__info__include=False,
        columns__edit=Column.edit(),
        columns__delete=Column.delete(),
    )

    new_artist = Form.create(
        title="New artist",
        auto__model=Artist,
        extra__redirect_to=".",
    )

    send_mail = Form(
        title="Send mail to all artists",
        fields__template=Field.choice_queryset(
            choices=MailTemplate.objects.filter(type="all_artists")
        ),
        actions__preview=Action.primary(
            display_name="Preview", post_handler=handle_send_mail
        ),
    )


class ArtistEditForm(Form):
    artist = Form.edit(
        auto__model=Artist,
        instance=lambda pk, **_: Artist.objects.get(pk=pk),
        fields__comments__input__attrs__rows=10,
        fields__info__input__attrs__rows=10,
    )

    links = EditTable(
        auto__model=Link,
        page_size=10,
        rows=lambda pk, **_: Link.objects.filter(artist__pk=pk),
        columns__artist__field=Field.non_rendered(
            initial=lambda pk, **_: Artist.objects.get(pk=pk)
        ),
        columns__type__field__include=True,
        columns__url__field__include=True,
        columns__delete=EditColumn.delete(),
        **{
            "attrs__data-iommi-edit-table-delete-with": "checkbox",
        }
    )

    class Meta:
        actions__submit__post_handler = save_nested_forms
        extra__redirect_to = lambda **_: reverse("main_menu.artists")


class ArtistEdit(Page):
    artist = ArtistEditForm()

    send_mail = Form(
        title="Send mail",
        fields__template=Field.choice_queryset(
            choices=MailTemplate.objects.filter(type="single_artist")
        ),
        fields__artist=Field.hidden(initial=lambda pk, **_: pk),
        actions__preview=Action.primary(
            display_name="Preview", post_handler=handle_send_mail
        ),
    )


artist_delete = Form.delete(instance=lambda pk, **_: Artist.objects.get(pk=pk))
