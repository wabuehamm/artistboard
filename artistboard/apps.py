from django.apps import AppConfig
from django.template.loader import get_template
from iommi import Asset, Style, register_style, style_foundation


class ArtistboardConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "artistboard"

    def ready(self):
        register_style(
            "artistboard",
            Style(
                style_foundation.foundation,
                root__assets__skills_css=Asset(
                    tag="style",
                    text=get_template(template_name="style.css").render(dict()),
                ),
                root__assets__favicon=Asset(template="favicon.html"),
            ),
        )
