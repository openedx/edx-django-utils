Cookie consent
==============

Utilities for respecting user consent regarding different cookie categories.

"Cookie" is a shorthand here for various types of tracking and storage, but cookies are the main focus.

Configuration
-------------

Set ``COOKIE_CONSENT_SOURCE`` to the module and name of a subclass of ``ConsentSource``, either one provided by edx-django-utils or from another package. This class will be responsible for answering whether the user has consented to certain categories of cookies. Known values:

- ``edx_django_utils.cookie_consent.OnlyNecessary`` is the default and will only permit strictly necessary cookies.
- ``edx_django_utils.cookie_consent.OneTrustSource`` will read and interpret the cookie set by OneTrust's consent UI.

Usage
-----

Call ``has_consented`` before setting cookies, passing it the request object and the category of cookie that would be set. Example::

    from edx_django_utils.cookie_consent import has_consented

    def set_referrer(request, ...):
        if has_consented(request, 'tracking'):
            request.set_cookie(...)
