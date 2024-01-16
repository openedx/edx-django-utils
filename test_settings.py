"""
These settings are here to use during tests, because django requires them.

In a real-world use case, apps in this project are installed into other
Django applications, so these settings will not be used.
"""

from os.path import abspath, dirname, join


def root(*args):
    """
    Get the absolute path of the given path relative to the project root.
    """
    return join(abspath(dirname(__file__)), *args)


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "default.db",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    },
    "read_replica": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "read_replica.db",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    },
}

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "waffle",
    "edx_django_utils",
    "edx_django_utils.admin.tests",
    "edx_django_utils.user",
    'edx_django_utils.data_generation',
    'edx_django_utils.data_generation.tests',
)

LOCALE_PATHS = [root("edx_django_utils", "conf", "locale")]

ROOT_URLCONF = "edx_django_utils.urls"

SECRET_KEY = "insecure-secret-key"
