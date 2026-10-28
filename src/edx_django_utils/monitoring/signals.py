"""
Signals defined to support monitoring plugins.

Placing signals in this file (vs alternatives like /internal, or
signals/signals.py) provides a good public api for these signals.
"""
import django.dispatch

# The MonitoringSupportMiddleware sends these signals to enable plugging in
# outside monitoring capabilities. This is a useful capability because the
# MonitoringSupportMiddleware should be available in all Open edX services,
# and should be one of the first middleware (after RequestCacheMiddleware),
# allowing it access to monitor most requests (even those that fail or
# respond early in other middleware).
monitoring_support_process_request = django.dispatch.Signal()
monitoring_support_process_response = django.dispatch.Signal()
monitoring_support_process_exception = django.dispatch.Signal()
