"""
Custom path converter so Django URL patterns accept unicode-aware slugs.

Django's built-in `<slug:>` converter uses the regex `[-a-zA-Z0-9_]+`, which
rejects accented characters (à, ç, é, ã, …). Since our `Article.slug` is
generated with `slugify(title, allow_unicode=True)`, we need the URL layer
to accept the same character set the model produces.

Python's `\w` is unicode-aware by default, so `[-\w]+` matches letters in
any script plus digits and underscore — a drop-in superset of Django's slug
character class.
"""


class UnicodeSlugConverter:
    regex = r'[-\w]+'

    def to_python(self, value: str) -> str:
        return value

    def to_url(self, value: str) -> str:
        return value
