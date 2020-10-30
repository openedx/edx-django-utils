"""
Deprecated Middleware for backward-compatibility.

IMPORTANT: No new classes should be added to this file.
TODO: Remove this file once these classes are no longer used.

"""
import warnings

from edx_django_utils.monitoring.internal.code_owner.middleware import \
    CodeOwnerMonitoringMiddleware as InternalCodeOwnerMonitoringMiddleware
from edx_django_utils.monitoring.internal.utils import set_custom_attribute


class CodeOwnerMonitoringMiddleware(InternalCodeOwnerMonitoringMiddleware):
    """
    Deprecated class for handling middleware. Class has been moved to public API.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        msg = "Use 'edx_django_utils.monitoring.CodeOwnerMonitoringMiddleware' in place of " \
              "'edx_django_utils.monitoring.code_owner.middleware.CodeOwnerMonitoringMiddleware'."
        warnings.warn(msg, DeprecationWarning)
        set_custom_attribute('deprecated_code_owner_middleware', 'CodeOwnerMonitoringMiddleware')


class CodeOwnerMetricMiddleware(InternalCodeOwnerMonitoringMiddleware):
    """
    Deprecated class for handling middleware. Class has been renamed to CodeOwnerMonitoringMiddleware.
    """
    def __init__(self, *args, **kwargs):  # pragma: no cover
        super().__init__(*args, **kwargs)
        msg = "Use 'edx_django_utils.monitoring.CodeOwnerMonitoringMiddleware' in place of " \
              "'edx_django_utils.monitoring.code_owner.middleware.CodeOwnerMetricMiddleware'."
        warnings.warn(msg, DeprecationWarning)
        set_custom_attribute('deprecated_code_owner_middleware', 'CodeOwnerMetricMiddleware')
