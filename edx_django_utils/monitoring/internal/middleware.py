"""
Middleware for monitoring.

At this time, monitoring details can only be reported to New Relic.

"""
import logging
import platform
import warnings
from uuid import uuid4

import django
import psutil
import waffle  # pylint: disable=invalid-django-waffle-import
from django.utils.deprecation import MiddlewareMixin

from edx_django_utils.cache import RequestCache

log = logging.getLogger(__name__)
try:
    import newrelic.agent
except ImportError:  # pragma: no cover
    log.warning("Unable to load NewRelic agent module")
    newrelic = None  # pylint: disable=invalid-name


_DEFAULT_NAMESPACE = 'edx_django_utils.monitoring'
_REQUEST_CACHE_NAMESPACE = f'{_DEFAULT_NAMESPACE}.custom_attributes'


class DeploymentMonitoringMiddleware:
    """
    Middleware to record environment values at the time of deployment for each service.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.record_python_version()
        self.record_django_version()
        response = self.get_response(request)
        return response

    @staticmethod
    def record_django_version():
        """
        Record the installed Django version as custom attribute

        .. custom_attribute_name: django_version
        .. custom_attribute_description: The django version in use (e.g. '2.2.24').
           Set by DeploymentMonitoringMiddleware.
        """
        if not newrelic:  # pragma: no cover
            return
        _set_custom_attribute('django_version', django.__version__)

    @staticmethod
    def record_python_version():
        """
        Record the Python version as custom attribute

        .. custom_attribute_name: python_version
        .. custom_attribute_description: The Python version in use (e.g. '3.8.10').
           Set by DeploymentMonitoringMiddleware.
        """
        if not newrelic:  # pragma: no cover
            return
        _set_custom_attribute('python_version', platform.python_version())


class CachedCustomMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware batch reports cached custom attributes at the end of a request.

    Make sure to add below the request cache in MIDDLEWARE.

    This middleware will only call on the newrelic agent if there are any attributes
    to report for this request, so it will not incur any processing overhead for
    request handlers which do not record custom attributes.

    Note: New Relic adds custom attributes to events, which is what is being used here.

    """
    @classmethod
    def _get_attributes_cache(cls):
        """
        Get a request cache specifically for New Relic custom attributes.
        """
        return RequestCache(namespace=_REQUEST_CACHE_NAMESPACE)

    @classmethod
    def accumulate_attribute(cls, name, value):
        """
        Accumulate a custom attribute (name and value) in the attributes cache.
        """
        attributes_cache = cls._get_attributes_cache()
        cached_response = attributes_cache.get_cached_response(name)
        if cached_response.is_found:
            try:
                accumulated_value = value + cached_response.value
            except TypeError:
                _set_custom_attribute(
                    'error_adding_accumulated_metric',
                    'name={}, new_value={}, cached_value={}'.format(
                        name, repr(value), repr(cached_response.value)
                    )
                )
                return
        else:
            accumulated_value = value
        attributes_cache.set(name, accumulated_value)

    @classmethod
    def accumulate_metric(cls, name, value):  # pragma: no cover
        """
        Deprecated method replaced by accumulate_attribute.
        """
        msg = "Use 'accumulate_attribute' in place of 'accumulate_metric'."
        warnings.warn(msg, DeprecationWarning)
        _set_custom_attribute('deprecated_accumulate_metric', True)
        cls.accumulate_attribute(name, value)

    @classmethod
    def _batch_report(cls):
        """
        Report the collected custom attributes to New Relic.
        """
        if not newrelic:  # pragma: no cover
            return
        attributes_cache = cls._get_attributes_cache()
        for key, value in attributes_cache.data.items():
            _set_custom_attribute(key, value)

    # Whether or not there was an exception, report any custom NR attributes that
    # may have been collected.

    def process_response(self, request, response):
        """
        Django middleware handler to process a response
        """
        self._batch_report()
        return response

    def process_exception(self, request, exception):    # pylint: disable=W0613
        """
        Django middleware handler to process an exception
        """
        self._batch_report()


def _set_custom_attribute(key, value):
    """
    Sets monitoring custom attribute.

    Note: Can't use public method in ``utils.py`` due to circular reference.
    """
    if newrelic:  # pragma: no cover
        newrelic.agent.add_custom_parameter(key, value)


class MonitoringMemoryMiddleware(MiddlewareMixin):
    """
    Middleware for monitoring memory usage.

    Make sure to add below the request cache in MIDDLEWARE.
    """
    memory_data_key = 'memory_data'
    guid_key = 'guid_key'

    def process_request(self, request):
        """
        Store memory data to log later.
        """
        if self._is_enabled():
            self._cache.set(self.guid_key, str(uuid4()))
            log_prefix = self._log_prefix("Before", request)
            self._cache.set(self.memory_data_key, self._memory_data(log_prefix))

    def process_response(self, request, response):
        """
        Logs memory data after processing response.
        """
        if self._is_enabled():
            log_prefix = self._log_prefix("After", request)
            new_memory_data = self._memory_data(log_prefix)

            log_prefix = self._log_prefix("Diff", request)
            cached_memory_data_response = self._cache.get_cached_response(self.memory_data_key)
            old_memory_data = cached_memory_data_response.get_value_or_default(None)
            self._log_diff_memory_data(log_prefix, new_memory_data, old_memory_data)
        return response

    @property
    def _cache(self):
        """
        Namespaced request cache for tracking memory usage.
        """
        return RequestCache(namespace='monitoring_memory')

    def _log_prefix(self, prefix, request):
        """
        Returns a formatted prefix for logging for the given request.
        """
        # Note: After a celery task runs, the request cache is cleared. So if
        #   celery tasks are running synchronously (CELERY_ALWAYS _EAGER),
        #   "guid_key" will no longer be in the request cache when
        #   process_response executes.
        cached_guid_response = self._cache.get_cached_response(self.guid_key)
        cached_guid = cached_guid_response.get_value_or_default("without_guid")
        return f"{prefix} request '{request.method} {request.path} {cached_guid}'"

    def _memory_data(self, log_prefix):
        """
        Returns a dict with information for current memory utilization.
        Uses log_prefix in log statements.
        """
        machine_data = psutil.virtual_memory()

        process = psutil.Process()
        process_data = {
            'memory_info': process.memory_info(),
            'ext_memory_info': process.memory_info(),
            'memory_percent': process.memory_percent(),
            'cpu_percent': process.cpu_percent(),
        }

        log.info("%s Machine memory usage: %s; Process memory usage: %s", log_prefix, machine_data, process_data)
        return {
            'machine_data': machine_data,
            'process_data': process_data,
        }

    def _log_diff_memory_data(self, prefix, new_memory_data, old_memory_data):
        """
        Computes and logs the difference in memory utilization
        between the given old and new memory data.
        """
        def _vmem_used(memory_data):
            return memory_data['machine_data'].used

        def _process_mem_percent(memory_data):
            return memory_data['process_data']['memory_percent']

        def _process_rss(memory_data):
            return memory_data['process_data']['memory_info'].rss

        def _process_vms(memory_data):
            return memory_data['process_data']['memory_info'].vms

        if new_memory_data and old_memory_data:
            log.info(
                "%s Diff Vmem used: %s, Diff percent memory: %s, Diff rss: %s, Diff vms: %s",
                prefix,
                _vmem_used(new_memory_data) - _vmem_used(old_memory_data),
                _process_mem_percent(new_memory_data) - _process_mem_percent(old_memory_data),
                _process_rss(new_memory_data) - _process_rss(old_memory_data),
                _process_vms(new_memory_data) - _process_vms(old_memory_data),
            )

    def _is_enabled(self):
        """
        Returns whether this middleware is enabled.
        """
        return waffle.switch_is_active('edx_django_utils.monitoring.enable_memory_middleware')
