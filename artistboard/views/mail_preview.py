from smtplib import SMTPException
from django.http import HttpResponseRedirect
from django.template import Context
from django.template import Template as DjangoTemplate
from django.urls import reverse
from iommi import Action, Field, Form, Page, html
from markdown import markdown
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from artistboard.models import Artist, Event, MailTemplate, Season, Show


class MailBuilder:
    request = None
    template = None
    context = None

    def __init__(self, request):
        if MailBuilder.context == None:
            MailBuilder.request = request
            self.build_context()

    def build_context_single_season(self, season_pk):
        season = Season.objects.get(pk=season_pk)
        shows = Show.objects.filter(season__pk=season_pk)
        events = Event.objects.filter(show__season__pk=season_pk)
        artists = Artist.objects.all()
        return Context(dict(season=season, shows=shows, events=events, artists=artists))

    def build_context_single_artist(self, artist_pk):
        artist = Artist.objects.get(pk=artist_pk)
        booked_events = Event.objects.filter(booked_artist__pk=artist_pk)
        unbooked_events = Event.objects.filter(booked_artist=None)
        return Context(
            dict(
                artist=artist,
                booked_events=booked_events,
                unbooked_events=unbooked_events,
            )
        )

    def build_context_all_artists(self):
        return Context(dict(artists=Artist.objects.all()))

    def build_context(self):
        self.template = MailTemplate.objects.get(pk=self.request.GET["template"])
        match self.template.type:
            case "single_season":
                self.context = self.build_context_single_season(
                    self.request.GET["object"]
                )
            case "single_artist":
                self.context = self.build_context_single_artist(
                    self.request.GET["object"]
                )
            case "all_artists":
                self.context = self.build_context_all_artists()


def render_field(request, field):
    return DjangoTemplate(getattr(MailBuilder(request).template, field)).render(
        MailBuilder(request).context
    )


def handle_send_mail(form, request, page, **_):
    if settings.EMAIL_FROM == "":
        form.add_error("Error in the mail configuration. Missing from")
        return
    if form.is_valid():
        msg = EmailMultiAlternatives(
            render_field(request, "subject"),
            render_field(request, "body_text"),
            settings.EMAIL_FROM,
            render_field(request, "to").split(","),
        )

        template = MailTemplate.objects.get(pk=request.GET["template"])

        if template.cc is not None and render_field(request, "cc") != "":
            msg.cc = render_field(request, "cc").split(",")

        if template.bcc is not None and render_field(request, "bcc") != "":
            msg.bcc = render_field(request, "bcc").split(",")

        msg.attach_alternative(
            (
                markdown(render_field(request, "body_text"))
                if MailBuilder(request).template.use_markdown
                else render_field(request, "body_html")
            ),
            "text/html",
        )
        try:
            msg.send()
        except SMTPException as e:
            form.add_error(e)
            return

        page.extra["show_success"] = True
        return HttpResponseRedirect(
            reverse(
                "mail-preview",
                query=dict(
                    template=request.GET["template"], object=request.GET["object"]
                ),
            )
        )


def handle_show_success_onetime(page, **_):
    found = page.extra["show_success"]
    page.extra["show_success"] = False
    return found


class MailPreview(Page):
    title = "Preview"
    success = html.div(
        attrs__class__callout=True,
        attrs__class__success=True,
        children=dict(message=html.p("Mail sent successfully.")),
        include=handle_show_success_onetime,
    )
    mail = Form(
        title="Mail",
        editable=False,
        fields__template=Field.hidden(
            initial=lambda request, **_: request.GET["template"]
        ),
        fields__object=Field.hidden(initial=lambda request, **_: request.GET["object"]),
        fields__to=Field.text(initial=lambda request, **_: render_field(request, "to")),
        fields__cc=Field.text(initial=lambda request, **_: render_field(request, "cc")),
        fields__bcc=Field.text(
            initial=lambda request, **_: render_field(request, "bcc")
        ),
        fields__subject=Field.text(
            initial=lambda request, **_: render_field(request, "subject")
        ),
        fields__body_text=Field.textarea(
            initial=lambda request, **_: render_field(request, "body_text"),
            input__attrs__rows=40,
        ),
        fields__body_html=Field.textarea(
            input__template=lambda request, **_: (
                DjangoTemplate(markdown(render_field(request, "body_text")))
                if MailBuilder(request).template.use_markdown
                else DjangoTemplate(render_field(request, "body_html"))
            ),
            input__attrs__rows=40,
        ),
        actions__send=Action.primary(
            display_name="Send", post_handler=handle_send_mail
        ),
    )

    class Meta:
        extra__show_success = False
