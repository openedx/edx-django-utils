"""
Tests for the various ConsentSource classes shipped with edx-django-utils.
"""

import ddt

from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings

from edx_django_utils.cookie_consent import has_consented


@ddt.ddt
class TestOneTrust(TestCase):

    @override_settings(COOKIE_CONSENT_SOURCE='edx_django_utils.cookie_consent.OneTrustSource')
    @ddt.data(
        # Missing
        (None,),
        # Well-formed inputs, as far as we care
        ('version=5.12.0&groups=C0001:1,C0002:1,C0003:1,C0004:0&AwaitingReconsent=false',),
        ('groups=C0001:1,C0002:1,C0003:1,C0004:0',),
        # Malformed input
        ('',),
        ('groups=',),
        ('groups=C0001:1,,C0002:0',),
        ('groups=C0001:1,C0002:2',),
        ('groups=C0001:1:,C0002:0',),
    )
    @ddt.unpack
    def testNecessary(self, ot_cookie):
        """
        'necessary' should always be allowed, with or without a valid consent cookie.
        """
        factory = RequestFactory()
        if ot_cookie is not None:
            factory.cookies['OptanonConsent'] = ot_cookie
        request = RequestFactory().request()

        assert has_consented(request, 'necessary') == True
