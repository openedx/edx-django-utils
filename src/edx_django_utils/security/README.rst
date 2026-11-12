Security Utils
##############

Common security utilities.

Content-Security-Policy middleware
**********************************

Add the middleware ``'edx_django_utils.security.csp.middleware.content_security_policy_middleware'`` near the beginning of your ``MIDDLEWARE`` list in order to add ``Content-Security-Policy`` and ``Content-Security-Policy-Report-Only`` headers. See ``csp/middleware.py`` for configuration and details.
