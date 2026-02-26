from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from iommi import Column, EditColumn, EditTable, Field, Form, Page, Table
from iommi.form import save_nested_forms

from artistboard.models import Artist, Link
from artistboard.views.mail_template import SendMailForm


class ArtistView(Page):
    artists = Table(
        title=_("Artists"),
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
        columns__opportunities=Column.link(
            display_name=_("Opportunities"),
            attr=None,
            cell__value=_("Opportunities"),
            cell__url=lambda row, **_: reverse("artist-event", kwargs={"pk": row.pk})
        ),
        query__form__fields__locked__initial=False,
        columns__info__include=False,
        columns__edit=Column.edit(),
        columns__delete=Column.delete(),
    )

    new_artist = Form.create(
        title=_("New artist"),
        auto__model=Artist,
        extra__redirect_to=".",
    )

    send_mail = SendMailForm(extra__template_type="all_artists")


class ArtistEditForm(Form):
    artist = Form.edit(
        title=_("Artist"),
        auto__model=Artist,
        instance=lambda pk, **_: Artist.objects.get(pk=pk),
        fields__comments__input__attrs__rows=10,
        fields__info__input__attrs__rows=10,
    )

    links = EditTable(
        title=_("Links"),
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


class ArtistSendMailForm(SendMailForm):
    object = Field.hidden(
        initial=lambda pk, **_: pk
    )

    class Meta:
        extra__template_type = "single_artist"


class ArtistEdit(Page):
    artist = ArtistEditForm()

    send_mail = ArtistSendMailForm()


artist_delete = Form.delete(instance=lambda pk, **_: Artist.objects.get(pk=pk))
