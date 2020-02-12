"""
Middleware for handling the storage, aggregation, and reporting of custom
metrics for monitoring.

At this time, the custom metrics can only be reported to New Relic.

This middleware will only call on the newrelic agent if there are any metrics
to report for this request, so it will not incur any processing overhead for
request handlers which do not record custom metrics.

"""
import logging
from uuid import uuid4

import psutil
import waffle
from django.utils.deprecation import MiddlewareMixin

from edx_django_utils.cache import RequestCache
from edx_django_utils.private_utils import _check_middleware_dependencies

log = logging.getLogger(__name__)
try:
    import newrelic.agent
except ImportError:
    log.warning("Unable to load NewRelic agent module")
    newrelic = None  # pylint: disable=invalid-name


_DEFAULT_NAMESPACE = 'edx_django_utils.monitoring'
_REQUEST_CACHE_NAMESPACE = '{}.custom_metrics'.format(_DEFAULT_NAMESPACE)


class MonitoringCustomMetricsMiddleware(MiddlewareMixin):
    """
    The middleware class for adding custom metrics.

    Make sure to add below the request cache in MIDDLEWARE.
    """

    def __init__(self, *args, **kwargs):
        super(MonitoringCustomMetricsMiddleware, self).__init__(*args, **kwargs)
        # checks proper dependency order as well.
        _check_middleware_dependencies(self, required_middleware=[
            'edx_django_utils.cache.middleware.RequestCacheMiddleware',
            'edx_django_utils.monitoring.middleware.MonitoringCustomMetricsMiddleware',
        ])

    @classmethod
    def _get_metrics_cache(cls):
        """
        Get a reference to the part of the request cache wherein we store New
        Relic custom metrics related to the current request.
        """
        return RequestCache(namespace=_REQUEST_CACHE_NAMESPACE)

    @classmethod
    def accumulate_metric(cls, name, value):
        """
        Accumulate a custom metric (name and value) in the metrics cache.
        """
        metrics_cache = cls._get_metrics_cache()
        metrics_cache.setdefault(name, 0)
        metrics_cache.set(name, value)

    @classmethod
    def _batch_report(cls):
        """
        Report the collected custom metrics to New Relic.
        """
        if not newrelic:
            return
        metrics_cache = cls._get_metrics_cache()
        for key, value in metrics_cache.data.items():
            newrelic.agent.add_custom_parameter(key, value)

    # Whether or not there was an exception, report any custom NR metrics that
    # may have been collected.

    def process_response(self, request, response):
        """
        Django middleware handler to process a response
        """
        self._batch_report()
        return response

    def process_exception(self, request, exception):
        """
        Django middleware handler to process an exception
        """
        self._batch_report()


class MonitoringMemoryMiddleware(MiddlewareMixin):
    """
    Middleware for monitoring memory usage.

    Make sure to add below the request cache in MIDDLEWARE.
    """
    memory_data_key = u'memory_data'
    guid_key = u'guid_key'

    def __init__(self, *args, **kwargs):
        super(MonitoringMemoryMiddleware, self).__init__(*args, **kwargs)
        # checks proper dependency order as well.
        _check_middleware_dependencies(self, required_middleware=[
            'edx_django_utils.cache.middleware.RequestCacheMiddleware',
            'edx_django_utils.monitoring.middleware.MonitoringMemoryMiddleware',
        ])

    def process_request(self, request):
        """
        Store memory data to log later.
        """
        if self._is_enabled():
            self._cache.set(self.guid_key, str(uuid4()))
            log_prefix = self._log_prefix(u"Before", request)
            self._cache.set(self.memory_data_key, self._memory_data(log_prefix))

    def process_response(self, request, response):
        """
        Logs memory data after processing response.
        """
        if self._is_enabled():
            log_prefix = self._log_prefix(u"After", request)
            new_memory_data = self._memory_data(log_prefix)

            log_prefix = self._log_prefix(u"Diff", request)
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
        # After a celery task runs, the request cache is cleared. So if celery
        # tasks are running synchronously (CELERY_ALWAYS _EAGER), "guid_key"
        # will no longer be in the request cache when process_response executes.
        cached_guid_response = self._cache.get_cached_response(self.guid_key)
        cached_guid = cached_guid_response.get_value_or_default(u"without_guid")
        return u"{} request '{} {} {}'".format(prefix, request.method, request.path, cached_guid)

    def _memory_data(self, log_prefix):
        """
        Returns a dict with information for current memory utilization.
        Uses log_prefix in log statements.
        """
        machine_data = psutil.virtual_memory()

        process = psutil.Process()
        process_data = {
            'memory_info': process.get_memory_info(),
            'ext_memory_info': process.get_ext_memory_info(),
            'memory_percent': process.get_memory_percent(),
            'cpu_percent': process.get_cpu_percent(),
        }

        log.info(u"%s Machine memory usage: %s; Process memory usage: %s", log_prefix, machine_data, process_data)
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
                u"%s Diff Vmem used: %s, Diff percent memory: %s, Diff rss: %s, Diff vms: %s",
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
        return waffle.switch_is_active(u'edx_django_utils.monitoring.enable_memory_middleware')
