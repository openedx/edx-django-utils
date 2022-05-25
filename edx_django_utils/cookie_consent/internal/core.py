"""
Core functions for user consent.
"""

import abc
import re
from functools import lru_cache

from django.conf import settings
from django.utils.module_loading import import_string


class ConsentSource(abc.ABC):
    """
    Marker class for all consent-data sources

    This is used to ensure that arbitrary classes cannot be instantiated by config.
    """
    @abc.abstractmethod
    def has_consented(self, request, category):
        """
        Returns True if this cookie category is allowed for this request.
        """
        pass


class AcceptAll(ConsentSource):
    """
    Static "source" that always says yes.

    This does not represent an actual consent decision, and would not be compliant
    with privacy regulations. It is provided only as a fallback for unconfigured
    deployments.
    """
    def has_consented(self, request, category):
        return True


class OnlyNecessary(ConsentSource):
    """
    Static sources that only says yes to the "strictly necessary" category.
    """
    def has_consented(self, request, category):
        return category == 'necessary'


class OneTrustSource(ConsentSource):
    groups_re = re.compile('(?:^|&)groups=([^&]*)(?:&|$)')

    def parse_cookie():
        match = groups_re.search(cookie)
        if not match:
            return False
        return {kv.split(':', 1) for kv in match[1].split(',') if ':' in kv}

    """
    Interprets OneTrust's consent cookies.
    """
    def has_consented(self, request, category):
        if category == 'necessary':
            return True

        cookie = request.COOKIES.get('OptanonConsent', None)
        if not cookie:
            return False

        categories = parse_cookie(cookie)
        return categories.get(category, False)


def load_consent_source(module_class):
    fallback = AcceptAll()

    if not module_class:
        return fallback

    try:
        cls = import_string(module_class)
    except BaseException:
        log.warn(f"Could not load class {module_class}; defaulting to AcceptAll.")
        return fallback

    if not issubclass(cls, ConsentSource):
        log.warn(f"Class {module_class} does not inherit from ConsentSource; defaulting to AcceptAll.")
        return fallback

    return cls()


load_consent_source_cached = lru_cache(load_consent_source)


def has_consented(request, category):
    # .. setting_name: COOKIE_CONSENT_SOURCE
    # .. setting_default: None
    # .. setting_description: Indicates the class to use for making decisions about cookie consent.
    #   The class must inherit from ``edx_django_utils.cookie_consent.ConsentSource`` and implement
    #   ``has_consented``, accepting a request object and a category string. If class cannot be
    #   found or is not specified, the AcceptAll class will be used, so that no restrictions are
    #   imposed (i.e. ``has_consented`` will always return ``True``).
    consent_source = load_consent_source_cached(getattr(settings, 'COOKIE_CONSENT_SOURCE', ''))
    return consent_source.has_consented(request, category)
