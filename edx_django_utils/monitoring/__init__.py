"""
Monitoring utilities public api

Does not include signals.py, which is also part of the public api.
See README.rst for additional details.
"""
from .internal.backends import DatadogBackend, NewRelicBackend, OpenTelemetryBackend, TelemetryBackend
from .internal.middleware import (
    CachedCustomMonitoringMiddleware,
    CookieMonitoringMiddleware,
    DeploymentMonitoringMiddleware,
    FrontendMonitoringMiddleware,
    MonitoringMemoryMiddleware,
    MonitoringSupportMiddleware
)
from .internal.transactions import ignore_transaction
from .internal.utils import (
    accumulate,
    function_trace,
    increment,
    record_exception,
    set_custom_attribute,
    set_custom_attributes_for_course_key,
    set_monitoring_transaction_name
)
# "set_custom_metric*" methods are deprecated
from .utils import set_custom_metric, set_custom_metrics_for_course_key
