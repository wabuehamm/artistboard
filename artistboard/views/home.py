from django.utils.translation import gettext_lazy as _
from iommi import Page, html


class HomePage(Page):
    header = html.header(
        children=dict(
            title=html.h1(_("artistboard")),
            subtitle=html.p(
                _("Artist and event management tool.")
            ),
        )
    )
    body_text = html.p(_("Welcome to the artistboard. Please select a menu option on the left."))
