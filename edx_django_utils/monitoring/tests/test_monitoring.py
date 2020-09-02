"""
Tests for custom monitoring.
"""
from django.test import TestCase, override_settings
from mock import call, patch

from edx_django_utils import monitoring
from edx_django_utils.cache import RequestCache
from edx_django_utils.monitoring.middleware import (
    CachedCustomMonitoringMiddleware,
    MonitoringCustomMetricsMiddleware,
    MonitoringMemoryMiddleware
)


class TestCustomMonitoringMiddleware(TestCase):
    """
    Test the monitoring_utils middleware and helpers
    """
    def setUp(self):
        super(TestCustomMonitoringMiddleware, self).setUp()
        RequestCache.clear_all_namespaces()

    @patch('newrelic.agent')
    @override_settings(MIDDLEWARE=[
        'edx_django_utils.cache.middleware.RequestCacheMiddleware',
        'edx_django_utils.monitoring.middleware.CachedCustomMonitoringMiddleware',
    ])
    def test_accumulate_and_increment(self, mock_newrelic_agent):
        """
        Test normal usage of collecting custom attributes and reporting to New Relic
        """
        monitoring.accumulate('hello', 10)
        monitoring.accumulate('world', 10)
        monitoring.accumulate('world', 10)
        monitoring.increment('foo')
        monitoring.increment('foo')

        # based on the attribute data above, we expect the following calls to newrelic:
        nr_agent_calls_expected = [
            call('hello', 10),
            call('world', 20),
            call('foo', 2),
        ]

        # fake a response to trigger attributes reporting
        CachedCustomMonitoringMiddleware().process_response(
            'fake request',
            'fake response',
        )

        # Assert call counts to newrelic.agent.add_custom_parameter()
        expected_call_count = len(nr_agent_calls_expected)
        measured_call_count = mock_newrelic_agent.add_custom_parameter.call_count
        self.assertEqual(expected_call_count, measured_call_count)

        # Assert call args to newrelic.agent.add_custom_parameter().  Due to
        # the nature of python dicts, call order is undefined.
        mock_newrelic_agent.add_custom_parameter.assert_has_calls(nr_agent_calls_expected, any_order=True)

    @patch('newrelic.agent')
    @override_settings(MIDDLEWARE=[
        'edx_django_utils.cache.middleware.RequestCacheMiddleware',
        'edx_django_utils.monitoring.middleware.MonitoringCustomMetricsMiddleware',
    ])
    def test_accumulate_with_illegal_value(self, mock_newrelic_agent):
        """
        Test monitoring accumulate with illegal value that can't be added.
        """
        monitoring.accumulate('hello', None)
        monitoring.accumulate('hello', 10)

        # based on the metric data above, we expect the following calls to newrelic:
        nr_agent_calls_expected = [
            call('hello', None),
            call('error_adding_accumulated_metric', 'name=hello, new_value=10, cached_value=None'),
        ]

        # fake a response to trigger metrics reporting
        MonitoringCustomMetricsMiddleware().process_response(
            'fake request',
            'fake response',
        )

        # Assert call counts to newrelic.agent.add_custom_parameter()
        expected_call_count = len(nr_agent_calls_expected)
        measured_call_count = mock_newrelic_agent.add_custom_parameter.call_count
        self.assertEqual(expected_call_count, measured_call_count)

        # Assert call args to newrelic.agent.add_custom_parameter().
        mock_newrelic_agent.add_custom_parameter.assert_has_calls(nr_agent_calls_expected, any_order=True)

    @override_settings(MIDDLEWARE=[
        'edx_django_utils.cache.middleware.RequestCacheMiddleware',
        'edx_django_utils.monitoring.middleware.CachedCustomMonitoringMiddleware',
    ])
    def test_cached_custom_monitoring_middleware_dependencies_success(self):
        CachedCustomMonitoringMiddleware()

    @override_settings(MIDDLEWARE=[
        'edx_django_utils.cache.middleware.RequestCacheMiddleware',
        'edx_django_utils.monitoring.middleware.MonitoringCustomMetricsMiddleware',
    ])
    def test_custom_metrics_middleware_dependencies_success(self):
        MonitoringCustomMetricsMiddleware()

    @override_settings(MIDDLEWARE=['some.Middleware'])
    def test_cached_custom_monitoring_middleware_dependencies_failure(self):
        with self.assertRaises(AssertionError):
            CachedCustomMonitoringMiddleware()

    @override_settings(MIDDLEWARE=[
        'edx_django_utils.cache.middleware.RequestCacheMiddleware',
        'edx_django_utils.monitoring.middleware.MonitoringMemoryMiddleware',
    ])
    def test_memory_middleware_dependencies_success(self):
        MonitoringMemoryMiddleware()

    @override_settings(MIDDLEWARE=['some.Middleware'])
    def test_memory_middleware_dependencies_failure(self):
        with self.assertRaises(AssertionError):
            MonitoringMemoryMiddleware()

    @patch('newrelic.agent')
    def test_get_current_transaction(self, mock_newrelic_agent):
        mock_newrelic_agent.current_transaction().name = 'fake-transaction'
        current_transaction = monitoring.get_current_transaction()
        self.assertEqual(current_transaction.name, 'fake-transaction')

    def test_get_current_transaction_without_newrelic(self):
        current_transaction = monitoring.get_current_transaction()
        self.assertEqual(current_transaction.name, None)
