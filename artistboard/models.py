from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Artist(models.Model):
    name = models.CharField(_("Name"), max_length=200)
    locked = models.BooleanField(_("Locked"))
    contact_name = models.CharField(_("Contact name"), max_length=200)
    contact_address = models.TextField(_("Contact address"), blank=True, null=True)
    contact_phone = models.CharField(_("Contact phone"), max_length=200, blank=True, null=True)
    contact_email = models.EmailField(_("Contact E-Mail"))
    style = models.CharField(_("Style"), max_length=200, blank=True, null=True)
    number_artists = models.PositiveSmallIntegerField(_("Number of artists"), null=True, default=0)
    comments = models.TextField(_("Comments"), blank=True, null=True)
    rating = models.PositiveSmallIntegerField(
        _("Rating"), null=True, default=0, help_text=_("Rating of 5 stars")
    )
    info = models.TextField(_("Artist info"), blank=True, null=True)
    image = models.ImageField(_("Image"), blank=True, null=True)

    class Meta:
        verbose_name = _("Artist")
        verbose_name_plural = _("Artists")

    def get_absolute_url(self):
        return reverse("artist-view", kwargs={"pk": self.pk})

    def __str__(self):
        return self.name

    def event_links(self):
        events = EventArtist.objects.filter(artist=self)
        return_value = map(
            lambda event_artist: "<a href=\"%s\">%s</a>" % (
                reverse("event-edit", kwargs={
                    "pk": event_artist.event.pk,
                }),
                event_artist.event,
            ), events)

        return ", ".join(return_value)


class Link(models.Model):
    artist = models.ForeignKey(Artist, verbose_name=_("Artist"), on_delete=models.CASCADE)
    type = models.CharField(
        _("Type"),
        max_length=200,
        choices=[
            ("website", "Website"),
            ("fediverse", "Fediverse"),
            ("instagram", "Instagram"),
            ("youtube", "Youtube"),
            ("facebook", "Facebook"),
            ("bandcamp", "Bandcamp"),
            ("soundcloud", "Soundcloud"),
            ("twitch", "Twitch"),
            ("spotify", "Spotify"),
        ],
    )
    url = models.URLField(_("URL"))

    class Meta:
        verbose_name = _("Link")
        verbose_name_plural = _("Links")

    def __str__(self):
        return self.url


class Todo(models.Model):
    todo = models.CharField(_("Todo"), max_length=200)
    description = models.TextField(_("Description"), blank=True, null=True)
    available_for = models.CharField(_("Available for"), choices=[("season", _("Season")), ("event", _("Event"))])

    class Meta:
        verbose_name = _("Todo")
        verbose_name_plural = _("Todos")

    def get_absolute_url(self):
        return reverse("todo-view", kwargs={"pk": self.pk})

    def __str__(self):
        return self.todo


class Season(models.Model):
    year = models.PositiveSmallIntegerField(_("Year"))

    class Meta:
        verbose_name = _("Season")
        verbose_name_plural = _("Seasons")

    def get_absolute_url(self):
        return reverse("season-view", kwargs={"pk": self.pk})

    def __str__(self):
        return str(self.year)


class SeasonTodo(models.Model):
    todo = models.ForeignKey(Todo, verbose_name=_("Todo"), on_delete=models.CASCADE)
    season = models.ForeignKey(Season, verbose_name=_("Season"), on_delete=models.CASCADE)
    done = models.BooleanField(_("Done"), default=False)

    class Meta:
        verbose_name = _("Season Todo")
        verbose_name_plural = _("Season Todos")

    def __str__(self):
        return "%s %s" % ("✔️" if self.done else "❌", self.todo.todo)


class Show(models.Model):
    season = models.ForeignKey(Season, verbose_name=_("Season"), on_delete=models.CASCADE)
    name = models.CharField(_("Name"), max_length=200)

    class Meta:
        verbose_name = _("Show")
        verbose_name_plural = _("Shows")

    def __str__(self):
        return "%s/%s" % (self.season.year, self.name)


class Event(models.Model):
    show = models.ForeignKey(Show, verbose_name=_("Show"), on_delete=models.CASCADE)
    start_date = models.DateField(_("Starts on"))
    start_time = models.TimeField(_("Starts at"))
    booked_artist = models.ForeignKey(Artist, verbose_name=_("Booked Artist"), on_delete=models.CASCADE, null=True)
    agreement = models.TextField(_("Agreement"), blank=True, null=True)
    required_free_tickets = models.PositiveSmallIntegerField(_("Required free tickets"), null=True)
    required_paid_tickets = models.PositiveSmallIntegerField(_("Required paid tickets"), null=True)

    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")

    def get_absolute_url(self):
        return reverse("event-view", kwargs={"pk": self.pk})

    def __str__(self):
        return "%s@%s:%s" % (self.show, self.start_date, self.start_time)

    def fetch_artist_count(self):
        artists = EventArtist.objects.filter(event=self)
        artist_count = []
        for artist in artists:
            if Event.objects.filter(booked_artist=artist.artist).count() > 0:
                continue
            artist_count.append(
                {
                    "pk": artist.artist.pk,
                    "name": artist.artist.name,
                    "count": EventArtist.objects.filter(
                        artist=artist.artist, event__booked_artist=None
                    ).count(),
                }
            )
        return sorted(artist_count, key=lambda artist: artist["count"])

    def booking_artists(self):
        artist_count = self.fetch_artist_count()
        return_value = map(
            lambda artist: "<a href=\"%s\">%s (%s)</a>" % (
                reverse("event-assign", kwargs={
                    "pk": self.pk,
                    "artist_pk": artist["pk"],
                }),
                artist["name"],
                artist["count"]
            ), artist_count
        )
        return ", ".join(return_value)

    @property
    def booking_least_events(self):
        artist_count = self.fetch_artist_count()

        if len(artist_count) > 0:
            return artist_count[0]["count"]

        return 99999


class EventTodo(models.Model):
    event = models.ForeignKey(Event, verbose_name=_("Event"), on_delete=models.CASCADE)
    todo = models.ForeignKey(Todo, verbose_name=_("Todo"), on_delete=models.CASCADE)
    done = models.BooleanField(_("Done"), default=False)

    class Meta:
        verbose_name = _("Event Todo")
        verbose_name_plural = _("Event Todos")

    def __str__(self):
        return "%s %s" % ("✔️" if self.done else "❌", self.todo.todo)


class EventArtist(models.Model):
    event = models.ForeignKey(Event, verbose_name=_("Event"), on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, verbose_name=_("Artist"), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Opportunity")
        verbose_name_plural = _("Opportunities")

    def __str__(self):
        return str(self.event)

    def get_absolute_url(self):
        return reverse("artist-event", kwargs={"pk": self.pk})


class MailTemplate(models.Model):
    name = models.CharField(_("Name"), max_length=200)
    type = models.CharField(
        _("Type"),
        choices=[
            ("single_season", _("Single season")),
            ("all_artists", _("All artists")),
            ("single_artist", _("Single artist")),
        ],
        help_text=_(
            "Single season will get a context of season, shows, events, artists. All Artists will get the context artists. Single artist will get the context artist, booked_events, unbooked_events and last_season."
        ),
    )
    subject = models.TextField(_("Subject"))
    to = models.TextField(_("To"))
    cc = models.TextField(_("CC"), blank=True, null=True)
    bcc = models.TextField(_("BCC"), blank=True, null=True)
    body_text = models.TextField(_("Body (Text)"), blank=True, null=True)
    body_html = models.TextField(_("Body (HTML)"), blank=True, null=True)
    use_markdown = models.BooleanField(
        _("Use markdown"),
        default=False,
        help_text=_("Use the markdown rendered version of the text body for the HTML body"),
    )

    class Meta:
        verbose_name = _("Mail template")
        verbose_name_plural = _("Mail templates")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("mail_template-view", kwargs={"pk": self.pk})
