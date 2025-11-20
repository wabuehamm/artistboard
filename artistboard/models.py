from django.db import models
from django.urls import reverse


class Artist(models.Model):
    name = models.CharField(max_length=200)
    locked = models.BooleanField()
    contact_name = models.CharField(max_length=200)
    contact_address = models.TextField(blank=True, null=True)
    contact_phone = models.CharField(max_length=200, blank=True, null=True)
    contact_email = models.EmailField()
    style = models.CharField(max_length=200, blank=True, null=True)
    number_artists = models.PositiveSmallIntegerField(null=True, default=0)
    comments = models.TextField(blank=True, null=True)
    rating = models.PositiveSmallIntegerField(
        null=True, default=0, help_text="Rating of 5 stars"
    )
    info = models.TextField(blank=True, null=True)
    image = models.ImageField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse("artist-view", kwargs={"pk": self.pk})

    def __str__(self):
        return self.name


class Link(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    type = models.CharField(
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
    url = models.URLField()

    def __str__(self):
        return self.url


class Todo(models.Model):
    todo = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    available_for = models.CharField(choices=[("season", "Season"), ("event", "Event")])

    def get_absolute_url(self):
        return reverse("todo-view", kwargs={"pk": self.pk})

    def __str__(self):
        return self.todo


class Season(models.Model):
    year = models.PositiveSmallIntegerField()

    def get_absolute_url(self):
        return reverse("season-view", kwargs={"pk": self.pk})

    def __str__(self):
        return str(self.year)


class SeasonTodo(models.Model):
    todo = models.ForeignKey(Todo, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    done = models.BooleanField(default=False)

    def __str__(self):
        return "%s %s" % ("✔️" if self.done else "❌", self.todo.todo)


class Show(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

    def __str__(self):
        return "%s/%s" % (self.season.year, self.name)


class Event(models.Model):
    show = models.ForeignKey(Show, on_delete=models.CASCADE)
    start_date = models.DateField("Starts on")
    start_time = models.TimeField("Starts at")
    booked_artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=True)
    agreement = models.TextField(blank=True, null=True)
    required_free_tickets = models.PositiveSmallIntegerField(null=True)
    required_paid_tickets = models.PositiveSmallIntegerField(null=True)

    def get_absolute_url(self):
        return reverse("event-view", kwargs={"pk": self.pk})

    def __str__(self):
        return "%s@%s:%s" % (self.show, self.start_date, self.start_time)


class EventTodo(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    todo = models.ForeignKey(Todo, on_delete=models.CASCADE)
    done = models.BooleanField(default=False)

    def __str__(self):
        return "%s %s" % ("✔️" if self.done else "❌", self.todo.todo)


class EventArtist(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.artist)


class MailTemplate(models.Model):
    name = models.CharField(max_length=200)
    type = models.CharField(
        choices=[
            ("single_season", "Single season"),
            ("all_artists", "All artists"),
            ("single_artist", "Single artist"),
        ],
        help_text="Single season will get a context of season, shows, events. All Artists will get the context artists. Single artist will get the context artist.",
    )
    subject = models.TextField()
    to = models.TextField()
    cc = models.TextField(blank=True, null=True)
    bcc = models.TextField(blank=True, null=True)
    body_text = models.TextField("Body (Text)", blank=True, null=True)
    body_html = models.TextField("Body (HTML)", blank=True, null=True)
    use_markdown = models.BooleanField(
        default=False,
        help_text="Use the markdown rendered version of the text body for the HTML body",
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("mail_template-view", kwargs={"pk": self.pk})
