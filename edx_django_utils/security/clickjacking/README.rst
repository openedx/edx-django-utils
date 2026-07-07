Security Utils
##############

Common security utilities.

Deprecated - Clickjacking middleware
************************************

Consider this deprecated as new projects should be using Content Security Policy headers instead.
However, this won't be removed until no openedx project depends on it anymore, specifically, edx-platform.
Please do not add this middleware to a project unless you have to use the ``X-Frame-Options`` header,
and do not add it outside the openedx github organization, as it may be removed in the future.

Clickjacking middleware
***********************

The preferred way to prevent clickjacking is to use the Content Security Policy headers.
In some legacy code where those headers are not used, it is required to instead use the older
header ``X-Frame-Options`` set either to ``DENY`` or to ``SAMEORIGIN``.
In any case, this middleware allows you both to set the ``X-Frame-Options`` header to any recognized value -
``DENY``, ``SAMEORIGIN``, ``ALLOW`` per django setting - but defaults to ``DENY``.
It also allows you to override the header for specific urls defined via regex.

- Add the middleware ``'edx_django_utils.security.clickjacking.middleware.EdxXFrameOptionsMiddleware'`` near the end of your ``MIDDLEWARE`` list.
- This will add an `X-Frame-Options` header to all responses.
- Add ``X_FRAME_OPTIONS = value`` to your django settings file with "value" being ``DENY``, ``SAMEORIGIN``, or ``ALLOW``.
- Optionally, add ``X_FRAME_OPTIONS_OVERRIDES = [[regex, value]]`` where ``[[regex, value]]`` is a list of
  pairs consisting of a regex that matches urls to override and a value that's one of ``DENY``, ``SAMEORIGIN``, and ``ALLOW``.
