from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.mail import send_mass_mail
from django.conf import settings


@receiver(pre_save, sender='articles.Article')
def notify_subscribers_on_publish(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    if old.status == 'published' or instance.status != 'published':
        return

    from apps.newsletter.models import NewsletterSubscriber
    subscribers = list(
        NewsletterSubscriber.objects.filter(is_active=True).values_list('email', flat=True)
    )
    if not subscribers:
        return

    site_url = getattr(settings, 'SITE_URL', 'http://localhost:5173')
    article_url = f"{site_url}/noticia/{instance.slug}"
    subject = f'[Interpop] Nova publicação: {instance.title}'
    body = (
        f'{instance.excerpt}\n\n'
        f'Leia o artigo completo: {article_url}\n\n'
        f'---\n'
        f'Para cancelar sua inscrição, acesse: {site_url}/unsubscribe/'
    )
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@interpop.com')

    messages = tuple(
        (subject, body, from_email, [email])
        for email in subscribers
    )
    try:
        send_mass_mail(messages, fail_silently=True)
    except Exception:
        pass
