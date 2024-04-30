"""
Telemetry abstraction and backends that implement it.

Only a certain subset of the monitoring functions have been made
configurable via this module.
"""

import logging
import sys
from abc import ABC, abstractmethod
from functools import lru_cache

from django.conf import settings
from django.dispatch import receiver
from django.test.signals import setting_changed
from django.utils.module_loading import import_string

log = logging.getLogger(__name__)

# The newrelic package used to not be part of the requirements files
# and so a try-import was used here. This situation is no longer true,
# but we're still preserving that pattern until someone feels like
# doing the work to remove it. (Should just be a major version bump
# and communication to anyone who might be specifically removing the
# package for some reason.)
#
# Ticket for just doing an unconditional import:
# https://github.com/openedx/edx-django-utils/issues/396
try:
    import newrelic.agent
except ImportError:  # pragma: no cover
    newrelic = None  # pylint: disable=invalid-name


class TelemetryBackend(ABC):
    """
    Base class for telemetry sinks.
    """
    @abstractmethod
    def set_attribute(self, key, value):
        """
        Set a key-value attribute on a span. This might be the current
        span or it might the root span of the process, depending on
        the backend.
        """

    @abstractmethod
    def record_exception(self):
        """
        Record the exception that is currently being handled.
        """

    @abstractmethod
    def initialize_celery_monitoring(self, *args, **kwargs):
        """
        Instrument celery to be monitored by the monitoring service.

        Optional kwargs:
        worker_process_init - required for open telemetry to integrate to the clery signal.
        Import from from celery.signals.
        """

class NewRelicBackend(TelemetryBackend):
    """
    Send telemetry to New Relic.

    https://docs.newrelic.com/docs/apm/agents/python-agent/python-agent-api/guide-using-python-agent-api/
    """
    def __init__(self):
        if newrelic is None:
            raise Exception("Could not load New Relic monitoring backend; package not present.")

    def set_attribute(self, key, value):
        # Sets attribute on the transaction, rather than the current
        # span, matching historical behavior. There is also an
        # `add_custom_span_attribute` that would better match
        # OpenTelemetry's behavior, which we could try exposing
        # through a new, more specific TelemetryBackend method.
        #
        # TODO: Update to newer name `add_custom_attribute`
        # https://docs.newrelic.com/docs/apm/agents/python-agent/python-agent-api/addcustomparameter-python-agent-api/
        newrelic.agent.add_custom_parameter(key, value)

    def record_exception(self):
        # TODO: Replace with newrelic.agent.notice_error()
        # https://docs.newrelic.com/docs/apm/agents/python-agent/python-agent-api/recordexception-python-agent-api/
        newrelic.agent.record_exception()

    def initialize_celery_monitoring(self, *args, **kwargs):
        pass


class OpenTelemetryBackend(TelemetryBackend):
    """
    Send telemetry via OpenTelemetry.

    Requirements to use:

    - Install `opentelemetry-api` and `opentelemetry-instrumentation-celery` Python packages.
    - Configure and initialize OpenTelemetry

    API reference: https://opentelemetry-python.readthedocs.io/en/latest/
    """
    # pylint: disable=import-outside-toplevel
    def __init__(self):
        # If import fails, the backend won't be used.
        from opentelemetry import trace
        from opentelemetry.instrumentation.celery import CeleryInstrumentor
        self.otel_trace = trace
        self.instrumentor = CeleryInstrumentor

    def set_attribute(self, key, value):
        # Sets the value on the current span, not necessarily the root
        # span in the process.
        self.otel_trace.get_current_span().set_attribute(key, value)

    def record_exception(self):
        self.otel_trace.get_current_span().record_exception(sys.exc_info()[1])

    def initialize_celery_monitoring(self, *args, **kwargs):
        worker_process_init = kwargs.get('worker_process_init', None)
        if worker_process_init is not None:
            @worker_process_init.connect(weak=False)
            def init_celery_tracing(*args, **kwargs):
                self.instrumentor().instrument()
        else:
            raise Exception(
                "the worker_process_init celery signal must be provided for OpenTelemetry to monitor celery tasks."
                )


class DatadogBackend(TelemetryBackend):
    """
    Send telemetry to Datadog via ddtrace.

    Requirements to use:

    - Install `ddtrace` Python package
    - Initialize ddtrace, either via ddtrace-run or ddtrace.auto

    API reference: https://ddtrace.readthedocs.io/en/stable/api.html
    """
    # pylint: disable=import-outside-toplevel
    def __init__(self):
        # If import fails, the backend won't be used.
        from ddtrace import patch, tracer
        self.dd_tracer = tracer
        self.patch = patch

    def set_attribute(self, key, value):
        if root_span := self.dd_tracer.current_root_span():
            root_span.set_tag(key, value)

    def record_exception(self):
        if span := self.dd_tracer.current_span():
            span.set_traceback()

    def initialize_celery_monitoring(self, *args, **kwargs):
        self.patch(celery=True)


# We're using an lru_cache instead of assigning the result to a variable on
# module load. With the default settings (pointing to a TelemetryBackend
# in this very module), this function can't be successfully called until
# the module finishes loading, otherwise we get a circular import error
# that will cause the backend to be dropped from the list.
@lru_cache
def configured_backends():
    """
    Produce a list of TelemetryBackend instances from Django settings.
    """
    # .. setting_name: OPENEDX_TELEMETRY
    # .. setting_default: ['edx_django_utils.monitoring.NewRelicBackend']
    # .. setting_description: List of telemetry backends to send data to. Allowable values
    #   are dotted module paths to classes implementing `edx_django_utils.monitoring.TelemetryBackend`,
    #   such as the built-in `NewRelicBackend`, `OpenTelemetryBackend`, and `DatadogBackend`
    #   (in the same module). For historical reasons, this defaults to just
    #   New Relic, and not all monitoring features will report to all backends (New Relic
    #   having the broadest support). Unusable options are ignored. Configuration
    #   of the backends themselves is via environment variables and system config files
    #   rather than via Django settings.
    backend_classes = getattr(settings, 'OPENEDX_TELEMETRY', None)
    if isinstance(backend_classes, str):
        # Prevent a certain kind of easy mistake.
        raise Exception("OPENEDX_TELEMETRY must be a list, not a string.")
    if backend_classes is None:
        backend_classes = ['edx_django_utils.monitoring.NewRelicBackend']

    backends = []
    for backend_class in backend_classes:
        try:
            cls = import_string(backend_class)
            if issubclass(cls, TelemetryBackend):
                backends.append(cls())
            else:
                log.warning(
                    f"Could not load OPENEDX_TELEMETRY option {backend_class!r}: "
                    f"{cls} is not a subclass of TelemetryBackend"
                )
        except BaseException as e:
            log.warning(f"Could not load OPENEDX_TELEMETRY option {backend_class!r}: {e!r}")

    return backends


@receiver(setting_changed)
def _reset_state(sender, **kwargs):  # pylint: disable=unused-argument
    """Reset caches when settings change during unit tests."""
    configured_backends.cache_clear()
