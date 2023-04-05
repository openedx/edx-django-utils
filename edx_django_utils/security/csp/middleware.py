"""
Middleware to add Content-Security-Policy and related headers.

The ``content_security_policy_middleware`` middleware function can add
``Content-Security-Policy``, ``Content-Security-Policy-Report-Only``, and
``Reporting-Endpoints`` HTTP response headers. This functionality is
configured by Django settings but is also gated behind a Waffle flag,
``cms.experimental.content-security-policy``.
"""
import re
import warnings

from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed
from edx_toggles.toggles import WaffleFlag


def _load_headers() -> dict:
    """
    Return a dict of headers to append to every response, based on settings.
    """
    # .. setting_name: CSP_ENFORCE
    # .. setting_default: None
    # .. setting_description: Content-Security-Policy header to attach to all responses.
    #   This should include everything but the ``report-to`` or ``report-uri`` clauses; those
    #   will be appended automatically according to the ``CSP_REPORTING_NAME`` and
    #   ``CSP_REPORTING_URI`` settings. Newlines are permitted and will be replaced with spaces.
    #   A trailing `;` is also permitted.
    # .. setting_warning: Setting the CSP header to too strict a value can cause your pages to
    #   break. It is strongly recommended that deployers start by using ``CSP_REPORT_ONLY`` (along
    #   with the reporting settings) and only move or copy the policies into ``CSP_ENFORCE`` after
    #   confirming that the received CSP reports only represent false positives. (The report-only
    #   and enforcement headers may be used at the same time.)
    enforce_policies = getattr(settings, 'CSP_ENFORCE', None)

    # .. setting_name: CSP_REPORT_ONLY
    # .. setting_default: None
    # .. setting_description: Content-Security-Policy-Report-Only header to attach to
    #   all responses. See ``CSP_ENFORCE`` for details.
    report_policies = getattr(settings, 'CSP_REPORT_ONLY', None)

    # .. setting_name: CSP_REPORTING_URI
    # .. setting_default: None
    # .. setting_description: Content-Security-Policy-Report-Only header to attach to
    #   all responses. See ``CSP_ENFORCE`` for details.
    reporting_uri = getattr(settings, 'CSP_REPORTING_URI', None)

    # .. setting_name: CSP_REPORTING_NAME
    # .. setting_default: None
    # .. setting_description: Used for CSP Level 3 reporting. This sets the name to use in the
    #   report-to CSP field and the Reporting-Endpoints header. This should generally be an
    #   alphanumeric string; other characters such as hyphen and underscore are also allowed.
    #   See https://www.rfc-editor.org/rfc/rfc8941.html#section-3.3.4 for full grammar.
    reporting_endpoint_name = getattr(settings, 'CSP_REPORTING_NAME', None)

    # RFC 8941 Token is a RFC 7230 that must start with ALPHA or *, and can also contain / and :.
    sfToken = "[a-zA-Z*][a-zA-Z0-9!#$%&'*+\\-.^_`|~\":/]*"
    if reporting_endpoint_name and not re.fullmatch(sfToken, reporting_endpoint_name):
        warnings.warn(
            "CSP_REPORTING_NAME ignored, as it contains disallowed characters. "
            "CSP Level 3 will not be in use."
        )
        reporting_endpoint_name = None

    if not enforce_policies and not report_policies:
        return {}

    headers = {}

    reporting_suffix = ''
    if reporting_uri:
        reporting_suffix = f"; report-uri {reporting_uri}"
        if reporting_endpoint_name:
            headers['Reporting-Endpoints'] = f'{reporting_endpoint_name}="{reporting_uri}"'
            reporting_suffix += f"; report-to {reporting_endpoint_name}"

    def clean_header(value):
        # Collapse any internal whitespace that contains a newline. This allows
        # writing the setting value as a multi-line string, which is useful for
        # CSP -- the values can be quite long.
        value = re.sub("\\s*\n\\s*", " ", value).strip()
        # Remove any trailing semicolon, which we allow (for convenience).
        # The CSP spec does not allow trailing semicolons or empty directives.
        value = re.sub("[;\\s]+$", "", value)
        return value

    if enforce_policies:
        headers['Content-Security-Policy'] = clean_header(enforce_policies) + reporting_suffix

    if report_policies:
        headers['Content-Security-Policy-Report-Only'] = clean_header(report_policies) + reporting_suffix

    return headers


def _append_headers(response_headers, more_headers):
    """
    Append to the response headers. If a header already exists, assume it is
    permitted to be multi-valued (comma-separated), and update the existing value.

    Arguments:
        response_headers: response.headers (or any dict-like object), to be modified
        more_headers: Dict of header names to values
    """
    for k, v in more_headers.items():
        if existing := response_headers.get(k):
            response_headers[k] = f"{existing}, {v}"
        else:
            response_headers[k] = v


# .. toggle_name: cms.experimental.content-security-policy
# .. toggle_implementation: WaffleFlag
# .. toggle_default: False
# .. toggle_description: Gates deployment of CSP headers. When disabled, Content-Security-Policy
#   and other related headers are not attached to the response. This is primarily intended for
#   allowing a gradual rollout on large sites, where even a report-only header can cause
#   trouble by overwhelming the report-collection server. When adding a new clause to
#   ``CSP_REPORT_ONLY``, this can be first set to 1% activation, then 10%, then to Everyone.
#   This should be set to Everyone except when rolling out new restrictions.
# .. toggle_use_cases: circuit_breaker
# .. toggle_creation_date: 2023-03-24
FLAG_CSP = WaffleFlag('cms.experimental.content-security-policy', module_name=__name__)


def content_security_policy_middleware(get_response):
    """
    Middleware that adds Content-Security-Policy and related headers, if enabled.

    This should be reasonably high up in the middleware chain, since it should
    apply to all responses.
    """
    # Constant across all requests, since they're based on static settings.
    csp_headers = _load_headers()
    if not csp_headers:
        raise MiddlewareNotUsed()  # tell Django to skip this middleware

    def middleware_handler(request):
        response = get_response(request)
        if FLAG_CSP.is_enabled():
            # Reporting-Endpoints, CSP, and CSP-RO can all be multi-valued
            # (comma-separated) headers, though the CSP spec says "SHOULD NOT"
            # for the latter two.
            _append_headers(response.headers, csp_headers)
        return response

    return middleware_handler
