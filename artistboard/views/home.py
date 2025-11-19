from iommi import Page, html


class HomePage(Page):
    header = html.header(
        children=dict(
            title=html.h1("artistboard"),
            subtitle=html.p(
                "Artist and event management tool."
            ),
        )
    )
    body_text = "Welcome to the artistboard. Please select a menu option on the left."
