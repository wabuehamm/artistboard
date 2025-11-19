from django.urls import reverse
from iommi import Column, Form, Page, Table

from ..models import MailTemplate
from iommi.form import save_nested_forms


class MailTemplateView(Page):
    mail_templates = Table(
        auto__model=MailTemplate,
        page_size=10,
        columns__edit=Column.edit(),
        columns__delete=Column.delete(),
        columns__body_text__include=False,
        columns__body_html__include=False,
        columns__use_markdown__include=False,
    )
    new_mail_template = Form.create(
        title="New mail template",
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
