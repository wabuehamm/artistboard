from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from iommi import Column, Form, Page, Table, Action
from iommi.form import save_nested_forms, Field

from ..models import MailTemplate


class MailTemplateView(Page):
    mail_templates = Table(
        title=_("Mail templates"),
        auto__model=MailTemplate,
        page_size=10,
        columns__edit=Column.edit(),
        columns__delete=Column.delete(),
        columns__body_text__include=False,
        columns__body_html__include=False,
        columns__use_markdown__include=False,
    )
    new_mail_template = Form.create(
        title=_("New mail template"),
        auto__model=MailTemplate,
        extra__redirect_to=".",
        fields__subject__input__attrs__rows=3,
        fields__to__input__attrs__rows=3,
        fields__cc__input__attrs__rows=3,
        fields__bcc__input__attrs__rows=3,
        fields__body_text__input__attrs__rows=40,
        fields__body_html__input__attrs__rows=40,
    )


class MailTemplateEdit(Form):
    mail_template = Form.edit(
        title=_("Mail template"),
        auto__model=MailTemplate,
        instance=lambda pk, **_: MailTemplate.objects.get(pk=pk),
        fields__subject__input__attrs__rows=3,
        fields__to__input__attrs__rows=3,
        fields__cc__input__attrs__rows=3,
        fields__bcc__input__attrs__rows=3,
        fields__body_text__input__attrs__rows=40,
        fields__body_html__input__attrs__rows=40,
    )

    class Meta:
        actions__submit__post_handler = save_nested_forms
        extra__redirect_to = lambda **_: reverse("main_menu.mail_templates")


mail_template_delete = Form.delete(
    instance=lambda pk, **_: MailTemplate.objects.get(pk=pk)
)


def handle_send_mail(form, **_):
    if form.is_valid():
        if "object" in form.fields:
            return HttpResponseRedirect(
                reverse(
                    "mail-preview",
                    query=dict(
                        object=form.fields["object"].value,
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


class SendMailForm(Form):
    title = _("Send mail")
    template = Field.choice_queryset(
        display_name=_("Template"),
        model=MailTemplate,
        choices=lambda form, **_: MailTemplate.objects.filter(type=form.extra.template_type)
    )

    class Meta:
        actions__preview = Action.primary(
            display_name=_("Preview"), post_handler=handle_send_mail
        )
