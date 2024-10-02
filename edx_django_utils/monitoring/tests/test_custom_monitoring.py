"""
Tests for CachedCustomMonitoringMiddleware and associated utilities.

Note: See test_middleware.py for the rest of the middleware tests.
"""
from unittest.mock import Mock, call, patch

import ddt
from django.test import TestCase, override_settings

from edx_django_utils.cache import RequestCache
from edx_django_utils.monitoring import MonitoringSupportMiddleware, accumulate, get_current_transaction, increment

from ..middleware import CachedCustomMonitoringMiddleware as DeprecatedCachedCustomMonitoringMiddleware
from ..middleware import MonitoringCustomMetricsMiddleware as DeprecatedMonitoringCustomMetricsMiddleware
from ..utils import accumulate as deprecated_accumulate
from ..utils import increment as deprecated_increment
from ..utils import set_custom_attribute as deprecated_set_custom_attribute
from ..utils import set_custom_attributes_for_course_key as deprecated_set_custom_attributes_for_course_key


@ddt.ddt
class TestCustomMonitoringMiddleware(TestCase):
    """
    Test the monitoring_utils middleware and helpers
    """
    def setUp(self):
        super().setUp()
        self.mock_response = Mock()
        RequestCache.clear_all_namespaces()

    @patch('newrelic.agent')
    @ddt.data(
        (MonitoringSupportMiddleware, False, 'process_response'),
        (MonitoringSupportMiddleware, False, 'process_exception'),
        (DeprecatedCachedCustomMonitoringMiddleware, True, 'process_response'),
        (DeprecatedMonitoringCustomMetricsMiddleware, True, 'process_response'),
    )
    @ddt.unpack
    def test_accumulate_and_increment(
            self, cached_monitoring_middleware_class, is_deprecated, middleware_method_name, mock_newrelic_agent
    ):
        """
        Test normal usage of collecting custom attributes and reporting to New Relic
        """
        accumulate('hello', 10)
        accumulate('world', 10)
        accumulate('world', 10)
        increment('foo')
        increment('foo')

        # based on the attribute data above, we expect the following calls to newrelic:
        nr_agent_calls_expected = [
            call('hello', 10),
            call('world', 20),
            call('foo', 2),
        ]

        # fake a response to trigger attributes reporting
        middleware_method = getattr(cached_monitoring_middleware_class(self.mock_response), middleware_method_name)
        middleware_method(
            'fake request',
            'fake response',
        )

        # Assert call counts to newrelic.agent.add_custom_parameter()
        expected_call_count = len(nr_agent_calls_expected)
        if is_deprecated:
            expected_call_count += 1
        measured_call_count = mock_newrelic_agent.add_custom_parameter.call_count
        self.assertEqual(expected_call_count, measured_call_count)

        # Assert call args to newrelic.agent.add_custom_parameter().  Due to
        # the nature of python dicts, call order is undefined.
        mock_newrelic_agent.add_custom_parameter.assert_has_calls(nr_agent_calls_expected, any_order=True)

    @patch('newrelic.agent')
    @ddt.data(
        (MonitoringSupportMiddleware, False),
        (DeprecatedCachedCustomMonitoringMiddleware, True),
        (DeprecatedMonitoringCustomMetricsMiddleware, True),
    )
    @ddt.unpack
    def test_accumulate_with_illegal_value(
            self, cached_monitoring_middleware_class, is_deprecated, mock_newrelic_agent
    ):
        """
        Test monitoring accumulate with illegal value that can't be added.
        """
        accumulate('hello', None)
        accumulate('hello', 10)

        # based on the metric data above, we expect the following calls to newrelic:
        nr_agent_calls_expected = [
            call('hello', None),
            call('error_adding_accumulated_metric', 'name=hello, new_value=10, cached_value=None'),
        ]

        self.mock_response = Mock()
        # fake a response to trigger metrics reporting
        cached_monitoring_middleware_class(self.mock_response).process_response(
            'fake request',
            'fake response',
        )

        # Assert call counts to newrelic.agent.add_custom_parameter()
        expected_call_count = len(nr_agent_calls_expected)
        if is_deprecated:
            expected_call_count += 1
        measured_call_count = mock_newrelic_agent.add_custom_parameter.call_count
        self.assertEqual(expected_call_count, measured_call_count)

        # Assert call args to newrelic.agent.add_custom_parameter().
        mock_newrelic_agent.add_custom_parameter.assert_has_calls(nr_agent_calls_expected, any_order=True)

    @patch('ddtrace.Tracer.current_root_span')
    def test_error_tagging(self, mock_get_root_span):
        # Ensure that we continue to support tagging exceptions in MonitoringSupportMiddleware.
        # This is only implemented for DatadogBackend at the moment.
        fake_exception = Exception()
        mock_root_span = Mock()
        mock_get_root_span.return_value = mock_root_span
        with override_settings(OPENEDX_TELEMETRY=['edx_django_utils.monitoring.DatadogBackend']):
            MonitoringSupportMiddleware(self.mock_response).process_exception(
                'fake request', fake_exception
            )
            mock_root_span.set_exc_info.assert_called_with(
                type(fake_exception), fake_exception, fake_exception.__traceback__
            )

    @patch('newrelic.agent')
    def test_get_current_transaction(self, mock_newrelic_agent):
        mock_newrelic_agent.current_transaction().name = 'fake-transaction'
        current_transaction = get_current_transaction()
        self.assertEqual(current_transaction.name, 'fake-transaction')

    def test_get_current_transaction_without_newrelic(self):
        current_transaction = get_current_transaction()
        self.assertEqual(current_transaction.name, None)

    @patch('edx_django_utils.monitoring.utils.internal_accumulate')
    def test_deprecated_accumulate(self, mock_accumulate):
        deprecated_accumulate('key', 1)
        mock_accumulate.assert_called_with('key', 1)

    @patch('edx_django_utils.monitoring.utils.internal_increment')
    def test_deprecated_increment(self, mock_increment):
        deprecated_increment('key')
        mock_increment.assert_called_with('key')

    @patch('edx_django_utils.monitoring.utils.internal_set_custom_attribute')
    def test_deprecated_set_custom_attribute(self, mock_set_custom_attribute):
        deprecated_set_custom_attribute('key', True)
        mock_set_custom_attribute.assert_called_with('key', True)

    @patch('edx_django_utils.monitoring.utils.internal_set_custom_attributes_for_course_key')
    def test_deprecated_set_custom_attributes_for_course_key(self, mock_set_custom_attributes_for_course_key):
        deprecated_set_custom_attributes_for_course_key('key')
        mock_set_custom_attributes_for_course_key.assert_called_with('key')
