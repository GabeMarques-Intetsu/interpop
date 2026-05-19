from django.apps import AppConfig


class ArticlesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.articles'
    verbose_name = 'Artigos'

    def ready(self) -> None:
        # Wire up signals that auto-notify newsletter subscribers
        # when an article is published.
        from . import signals  # noqa: F401
