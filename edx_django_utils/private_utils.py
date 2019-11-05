"""
Private utility methods.

These utilities are designated for internal use only (i.e. inside
edx-django-utils).  In some cases, these utilities could be elevated to public
methods once they get some burn-in time and find a more permanent home in the
library.
"""
import django
from django.conf import settings


def _check_middleware_dependencies(concerned_object, required_middleware):
    """
    Check required middleware dependencies exist and in the correct order.

    Args:
        concerned_object (object): The object for which the required
            middleware is being checked. This is used for error messages only.
        required_middleware (list of String): An ordered list representing the
            required middleware to be checked.

    Usage:
        Add in __init__ method to a Middleware class to have its dependencies
        checked on startup.

        def __init__(self):
            super(SomeMiddleware, self).__init__()
            _check_middleware_dependencies(self, required_middleware=[
                'edx_django_utils.cache.middleware.RequestCacheMiddleware',
            ])

    Raises:
        AssertionError if the provided dependencies don't appear in
            MIDDLEWARE in the correct order.

    """
    declared_middleware = getattr(settings, 'MIDDLEWARE', None)
    if declared_middleware is None and django.VERSION[0] < 2:
        declared_middleware = settings.MIDDLEWARE_CLASSES  # Pre-Django 2 support

    # Filter out all the middleware except the ones we care about for ordering.
    matching_middleware = [mw for mw in declared_middleware if mw in required_middleware]
    if required_middleware != matching_middleware:
        raise AssertionError(
            "{} requires middleware order {} but matching middleware was {}".format(
                concerned_object, required_middleware, matching_middleware
            )
        )
