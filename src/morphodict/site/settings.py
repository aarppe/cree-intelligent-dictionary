"""
Default common django settings for morphodict applications

To be used as,

    from morphodict.site.settings import *

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
import secrets

from environs import Env

from . import base_dir_setup
from .hostutils import HOSTNAME
from .save_secret_key import save_secret_key

BASE_DIR = base_dir_setup.get_base_dir()


# Read environment variables from project .env, if it exists
# See: https://github.com/sloria/environs#readme
env = Env()
env.read_env()

################################# Core Django Settings #################################

SECRET_KEY = env("SECRET_KEY", default=None)

if SECRET_KEY is None:
    # Generate a new key and save it!
    SECRET_KEY = save_secret_key(secrets.token_hex())

# Debug is default to False
# Turn it to True in development
DEBUG = env.bool("DEBUG", default=False)

# Application definition

# Individual sites SHOULD register their own apps by using:
#
#     INSTALLED_APPS.insert(0, "{source}{target}.app")
#
# Why .insert(0, ...)?
# Because Django's default template loader will use the template it finds **FIRST**
# in the app list.
# See: https://docs.djangoproject.com/en/3.2/ref/templates/api/#django.template.loaders.app_directories.Loader
INSTALLED_APPS = [
    # Django core apps:
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "morphodict.runserver",
    # WhiteNoise nostatic HAS to come before Django's staticfiles
    # See: http://whitenoise.evans.io/en/stable/django.html#using-whitenoise-in-development
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django_js_reverse",
    # Internal apps
    # TODO: our internal app organization is kind of a mess 🙃
    "CreeDictionary.API.apps.APIConfig",
    "CreeDictionary.CreeDictionary.apps.CreeDictionaryConfig",
    "CreeDictionary.cvd",
    "CreeDictionary.search_quality",
    "CreeDictionary.phrase_translate",
    "CreeDictionary.morphodict.apps.MorphodictConfig",
    "CreeDictionary.DatabaseManager",
    "morphodict.lexicon",
    # This comes last so that other apps can override templates
    "django.contrib.admin",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Static files with WhiteNoise:
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "morphodict.site.securemiddleware.set_secure_headers",
]

ROOT_URLCONF = "CreeDictionary.CreeDictionary.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "CreeDictionary.CreeDictionary.context_processors.display_options",
                "morphodict.lexicon.context_processors.language_pair",
                "morphodict.preference.context_processors.preferences",
            ]
        },
    }
]

# Custom settings

# Apps that have non-admin users typically have a stylized login page, but
# we only have admin logins. This setting will redirect to the admin login
# page if an anonymous user requests a page that requires permissions.
LOGIN_URL = "/admin/login"


# GitHub Actions and other services set CI to `true`
CI = env.bool("CI", default=False)

# Use existing test database (required for running unit tests and integration tests!)
USE_TEST_DB = env.bool("USE_TEST_DB", default=False)

# The Django debug toolbar is a great help when... you know... debugging Django,
# but it has a few issues:
#  - the middleware SIGNIFICANTLY increases request times
#  - the debug toolbar adds junk on the DOM, which may interfere with end-to-end tests
#
# The reasonable default is to enable it on development machines and let the developer
# opt out of it, if needed.
ENABLE_DJANGO_DEBUG_TOOLBAR = env.bool("ENABLE_DJANGO_DEBUG_TOOLBAR", default=DEBUG)

# The debug toolbar should ALWAYS be turned off:
#  - when DEBUG is disabled
#  - in CI environments
if not DEBUG or CI:
    ENABLE_DJANGO_DEBUG_TOOLBAR = False

# configure tools for development, CI, and production
if DEBUG and ENABLE_DJANGO_DEBUG_TOOLBAR:
    # enable django-debug-toolbar for development
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.insert(
        0, "debug_toolbar.middleware.DebugToolbarMiddleware"
    )  # middleware order is important

    # works with django-debug-toolbar app
    DEBUG_TOOLBAR_CONFIG = {
        # Toolbar options
        "SHOW_COLLAPSED": True,  # collapse the toolbar by default
    }

if DEBUG:
    # This is also used by django.template.context_processors.debug
    INTERNAL_IPS = ["127.0.0.1"]

# Used for verification with https://search.google.com/search-console
GOOGLE_SITE_VERIFICATION = "91c4e691b449e7e3"

if DEBUG:
    ALLOWED_HOSTS = ["*"]
else:  # pragma: no cover
    ALLOWED_HOSTS = [HOSTNAME, "localhost"]


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases


def defaultDatabasePath():
    """
    The default is to store the database in the repository folder. In
    production, docker can mount the database from elsewhere.

    Note that we deviate from the default slightly by putting the database
    in a dedicated `db` directory, and mounting the entire directory with
    docker, instead of only mounting the `.sqlite3` file.

    This is so that the additional `-shm` and `-wal` files that SQLite
    creates if running in write-ahead-logging aka WAL mode are kept
    together as one unit.

    This also helps out in some situations with swapping out database files
    that have had migrations applied offline. If `foo` is a file that is
    also a docker mount, and you `mv foo bar && touch foo` from outside the
    container, the container file `foo` now points at the outside `bar`.
    Things are more normal with directory mounts.
    """
    path = BASE_DIR / "db" / "db.sqlite3"
    return f"sqlite:///{path}"


if USE_TEST_DB:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.fspath(BASE_DIR / "db" / "test_db.sqlite3"),
        }
    }
else:
    DATABASES = {
        "default": (
            # The default SQLite timeout is 5 seconds, which can be too low and
            # give "Database is locked" errors when doing large backend updates
            # on a live system. Attempt to increase this.
            {"OPTIONS": {"timeout": 30}}
            | env.dj_db_url("DATABASE_URL", default=defaultDatabasePath())
        )
    }

# Django sites framework

# See: https://docs.djangoproject.com/en/2.2/ref/contrib/sites/#enabling-the-sites-framework
SITE_ID = 1

# SecurityMiddleware

# Send X-Content-Type-Options: nosniff header
# (prevents browser from guessing content type and doing unwise things)
# See: https://owasp.org/www-project-secure-headers/#x-content-type-options
SECURE_CONTENT_TYPE_NOSNIFF = True

# Do not allow embedding within an <iframe> ANYWHERE
# See: https://owasp.org/www-project-secure-headers/#x-frame-options
X_FRAME_OPTIONS = "DENY"


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = env("STATIC_URL", "/static/")

STATIC_ROOT = os.fspath(env("STATIC_ROOT", default=BASE_DIR / "collected-static"))

if DEBUG:
    # Use the default static storage backed for debug purposes.
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
else:
    # In production, use a manifest to encourage aggressive caching
    # Note requires `manage.py collectstatic`!
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Logging

log_level = env.log_level("LOG_LEVEL", default="INFO")
query_log_level = env.log_level("QUERY_LOG_LEVEL", default="INFO")

# To debug what the *actual* config ends up being, use the logging_tree package
# See https://stackoverflow.com/a/53058203/14558
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            # The handler should print anything that gets to it, so that
            # debugging can be enabled for specific loggers without also turning
            # on debug loggers for all of django/python
            "level": "NOTSET",
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": log_level,
    },
    "loggers": {
        # learn how different loggers are used in Django: https://docs.djangoproject.com/en/3.2/topics/logging/#id3
        "django": {
            "handlers": [],
            "level": log_level,
            "propagate": True,
        },
        "django.db.backends": {"level": query_log_level},
        # gensim is a little too chatty for my tastes in terms of printing
        # multiple lengthy INFO log messages when models are loaded. That’d be
        # fine for a server process, but it can get a bit much with management
        # commands and in notebooks.
        "gensim": {"level": "WARNING"},
    },
}

# Morphodict config

# We only apply affix search for user queries longer than the threshold length
AFFIX_SEARCH_THRESHOLD = 4
