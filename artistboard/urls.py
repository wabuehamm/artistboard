from django.urls import path

from .views import home, mail_template, event, artist, mail_preview, todos
from .views.season import season, booking_overview
from iommi.main_menu import MainMenu, M, EXTERNAL
from iommi.views import auth_views

menu_declaration = MainMenu(
    items=dict(
        home=M(
            icon="home",
            view=home.HomePage().as_view(),
        ),
        seasons=M(
            icon="calendar",
            view=season.SeasonView().as_view(),
            paths=[
                path("<int:pk>/", season.SeasonEdit().as_view(), name="season-view"),
                path(
                    "<int:pk>/edit/", season.SeasonEdit().as_view(), name="season-edit"
                ),
                path(
                    "<int:pk>/delete/",
                    season.season_delete.as_view(),
                    name="season-delete",
                ),
                path(
                    "<int:season_pk>/shows/<int:pk>/",
                    season.SeasonEdit().as_view(),
                    name="event-edit",
                ),
                path(
                    "<int:season_pk>/booking/",
                    booking_overview.BookingOverviewPage().as_view(),
                    name="booking-overview",
                ),
            ],
        ),
        events=M(
            icon="calendar-o",
            view=event.EventView().as_view(),
            paths=[
                path("<int:pk>/", event.EventEdit().as_view(), name="event-view"),
                path("<int:pk>/edit/", event.EventEdit().as_view(), name="event-edit"),
                path(
                    "<int:pk>/delete/",
                    event.event_delete.as_view(),
                    name="event-delete",
                ),
                path(
                    '<int:pk>/assign/<int:artist_pk>', event.EventEdit().as_view(), name="event-assign"
                )
            ],
        ),
        artists=M(
            icon="users",
            view=artist.ArtistView().as_view(),
            paths=[
                path("<int:pk>/", artist.ArtistView().as_view(), name="artist-view"),
                path(
                    "<int:pk>/edit/", artist.ArtistEdit().as_view(), name="artist-edit"
                ),
                path(
                    "<int:pk>/delete/",
                    artist.artist_delete.as_view(),
                    name="artist-delete",
                ),
            ],
        ),
        mail_templates=M(
            icon="envelope",
            view=mail_template.MailTemplateView().as_view(),
            paths=[
                path(
                    "<int:pk>/",
                    mail_template.MailTemplateView().as_view(),
                    name="mail_template-view",
                ),
                path(
                    "<int:pk>/edit/",
                    mail_template.MailTemplateEdit().as_view(),
                    name="mail_template-edit",
                ),
                path(
                    "<int:pk>/delete/",
                    mail_template.mail_template_delete.as_view(),
                    name="mail_template-delete",
                ),
            ],
        ),
        todos=M(
            icon="check",
            view=todos.TodoView().as_view(),
            paths=[
                path("<int:pk>/", todos.TodoView().as_view(), name="todo-view"),
                path("<int:pk>/edit/", todos.TodoEdit().as_view(), name="todo-edit"),
                path(
                    "<int:pk>/delete/", todos.todo_delete.as_view(), name="todo-delete"
                ),
            ],
        ),
        change_password=M(icon="key", view=EXTERNAL, url="/change_password"),
        logout=M(icon="sign-out", view=EXTERNAL, url="/logout"),
    )
)

urlpatterns = menu_declaration.urlpatterns() + [
    path("mail", mail_preview.MailPreview().as_view(), name="mail-preview"),
    path("", auth_views()),
]
