from django.apps import AppConfig


class NewsletterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name               = 'apps.newsletter'
    label              = 'newsletter'
    # `ready()` removido com a deleção de `signals.py`: o signal de
    # notificação de publicação vive em `apps.articles.signals` (versão
    # canônica, com template HTML, service layer e logger estruturado).
    # A versão antiga em `apps.newsletter.signals` duplicava o mesmo
    # evento com texto puro + `except: pass` — cada publicação enviava
    # DOIS emails distintos por subscriber. Bug C2 do Improvement-system §11.1.
