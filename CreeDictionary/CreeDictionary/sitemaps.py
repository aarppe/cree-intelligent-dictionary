#!/usr/bin/env python3

from API.models import Wordform
from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class WordformSitemap(Sitemap):
    """
    Make heads available on world.
    """

    def items(self):
        return Wordform.objects.filter(is_lemma=True)


class StaticViewSitemap(Sitemap):
    """
    Index static pages too!

    Note that the 'items' list needs to be manually maintained :/

    See: https://docs.djangoproject.com/en/2.2/ref/contrib/sitemaps/#sitemap-for-static-views
    """

    def items(self):
        return ["index", "about", "contact-us"]

    def location(self, item):
        return reverse(f"cree-dictionary-{item}")


sitemaps = {
    "static": StaticViewSitemap,
    "words": WordformSitemap,
}
