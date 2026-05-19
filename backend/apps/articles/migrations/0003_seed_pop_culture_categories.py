"""
Reseed the Category vocabulary for the editorial pivot of Interpop:
the project repositions itself as critical analysis of Soft Power and the
hegemony of pop culture in international relations.

Forward:
    - Creates the 5 new editorial categories (idempotent via get_or_create).
    - Removes legacy categories that are no longer part of the new vocabulary
      AND have no articles attached. Slots with articles are left untouched
      so this migration is always safe to apply.

Backward:
    - Mirror image: removes the new categories (only if empty) and recreates
      the legacy ones.

Verified before authoring: at the time of writing, the database had 6 legacy
categories with zero articles each, so the cleanup runs with no data loss.
"""

from django.db import migrations
from django.utils.text import slugify


NEW_CATEGORIES = [
    "Música",
    "Moda",
    "Cinema",
    "Literatura",
    "Cultura Digital",
]

LEGACY_CATEGORIES = [
    "Política",
    "Tecnologia",
    "Cultura",
    "Negócios",
    "Internacional",
    "Economia",
]


def _slug(name: str) -> str:
    return slugify(name, allow_unicode=True)


def _sync(apps, additions, removals):
    """Idempotent sync: create `additions`, delete `removals` if empty."""
    Category = apps.get_model("articles", "Category")

    for name in additions:
        Category.objects.get_or_create(
            slug=_slug(name),
            defaults={"name": name},
        )

    for name in removals:
        slug = _slug(name)
        # Only delete if it exists AND has no attached articles. The FK is
        # SET_NULL, so deletion would not raise — but we still refuse to lose
        # any author intent silently.
        try:
            cat = Category.objects.get(slug=slug)
        except Category.DoesNotExist:
            continue
        if cat.articles.count() == 0:
            cat.delete()


def forward(apps, schema_editor):
    _sync(apps, additions=NEW_CATEGORIES, removals=LEGACY_CATEGORIES)


def backward(apps, schema_editor):
    _sync(apps, additions=LEGACY_CATEGORIES, removals=NEW_CATEGORIES)


class Migration(migrations.Migration):

    dependencies = [
        ("articles", "0002_initial"),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]
