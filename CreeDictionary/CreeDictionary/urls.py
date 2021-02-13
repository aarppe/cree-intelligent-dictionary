"""
Definition of urls for CreeDictionary.
"""

import logging
import os

import API.views as api_views
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django_js_reverse.views import urls_js

from CreeDictionary import views

logger = logging.getLogger(__name__)

# 2019/May/21 Matt Yan:

# The reason to have different rules in development/production:

# static file urls / web-page urls / API urls in this project all begin with "cree-dictionary"
# so that in production on server sapir, the cree-dictionary service can be proxy-ed by looking for
# initial "cree-dictionary" in the url.

# example url:
# http://sapir.artsrn.ualberta.ca/cree-dictionary/search/hello

# in development, though, the initial "cree-dictionary" is not needed, example:
# http://localhost:8000/search/hello
# Note: re_path here, for example "re_path("^(cree-dictionary/)?some/url")", isn't a good solution. It messes up with
# url reversion

# 2021-01-12 Eddie Antonio Santos:
#
# I'm in the process of fixing this on Sapir.
#
# This routing code needs to know how to handle both when SCRIPT_NAME is
# specified as '/cree-dictionary' and when it's not.
#
# Then, the Gunicorn config on Sapir must be changed to supply -v
# SCRIPT_NAME='/cree-dictionary' in its startup options.
#
# The following function, as well as any comments ands hacks associated with it can be
# deleted soon!


def running_on_sapir_without_script_name():  # pragma: no cover
    """
    No longer required.
    """
    return False


# TODO: Convert this to an idiomatic Django style when we drop support for
# Sapir
_urlpatterns = [
    # user interface
    ("", views.index, "cree-dictionary-index"),
    ("search", views.index, "cree-dictionary-search"),
    # DEPRECATED: this route 👇 is a permanent redirect to the route above ☝️
    (
        "search/<str:query_string>/",
        views.redirect_search,
        "cree-dictionary-index-with-query",
    ),
    # word is a user-friendly alternative for the linguistic term "lemma"
    (
        "word/<str:lemma_text>/",
        views.lemma_details,
        "cree-dictionary-index-with-lemma",
    ),
    ("about", views.about, "cree-dictionary-about"),
    ("contact-us", views.contact_us, "cree-dictionary-contact-us"),
    # internal use to render boxes of search results
    (
        "_search_results/<str:query_string>/",
        views.search_results,
        "cree-dictionary-search-results",
    ),
    # internal use to render paradigm and only the paradigm
    (
        "_paradigm_details/",
        views.paradigm_internal,
        "cree-dictionary-paradigm-detail",
    ),
    # cree word translation for click-in-text
    (
        "click-in-text/",
        api_views.click_in_text,
        "cree-dictionary-word-click-in-text-api",
    ),
    ("admin/", admin.site.urls, "admin"),
    (
        "",
        include("morphodict.urls"),
        "cree-dictionary-change-orthography",
    ),
    ("search-quality/", include("search_quality.urls"), "search_quality"),
]

# Add style debugger, but only in DEBUG mode!
if settings.DEBUG:
    _urlpatterns.append(("styles", views.styles, "styles"))

# XXX: ugly hack to make this work on a local instance and on Sapir
urlpatterns = []

for route, view, name in _urlpatterns:
    # kwarg `name` for url reversion in html/py/js code
    urlpatterns.append(path(route, view, name=name))

# magic that allows us to reverse urls in js  https://github.com/ierror/django-js-reverse
urlpatterns.append(url(fr"^jsreverse/$", urls_js, name="js_reverse"))

admin.site.site_url = "/"

if settings.DEBUG:
    # saves the need to `manage.py collectstatic` in development
    urlpatterns += staticfiles_urlpatterns()

    if settings.ENABLE_DJANGO_DEBUG_TOOLBAR:
        import debug_toolbar

        # necessary for debug_toolbar to work
        urlpatterns.append(path("__debug__/", include(debug_toolbar.urls)))
