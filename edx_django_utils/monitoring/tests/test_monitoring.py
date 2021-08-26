"""
Tests for custom monitoring.
"""
import re
from unittest.mock import Mock, call, patch

import ddt
from django.test import TestCase

from edx_django_utils.cache import RequestCache
from edx_django_utils.monitoring import (
    CachedCustomMonitoringMiddleware,
    DeploymentMonitoringMiddleware,
    accumulate,
    get_current_transaction,
    increment,
    record_exception
)

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
        RequestCache.clear_all_namespaces()

    @patch('newrelic.agent')
    @ddt.data(
        (CachedCustomMonitoringMiddleware, False, 'process_response'),
        (CachedCustomMonitoringMiddleware, False, 'process_exception'),
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
        middleware_method = getattr(cached_monitoring_middleware_class(), middleware_method_name)
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
        (CachedCustomMonitoringMiddleware, False),
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

        # fake a response to trigger metrics reporting
        cached_monitoring_middleware_class().process_response(
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

    @patch('newrelic.agent.record_exception')
    def test_record_exception(self, mock_record_exception):
        record_exception()
        mock_record_exception.assert_called_once()


class TestDeploymentMonitoringMiddleware(TestCase):
    """
    Test the DeploymentMonitoringMiddleware functionalities
    """
    version_pattern = r'\d+(\.\d+){2}'

    def setUp(self):
        super().setUp()
        RequestCache.clear_all_namespaces()

    def _test_key_value_pair(self, function_call, key):
        """
        Asserts the function call key and value with the provided key and the default version_pattern
        """
        attribute_key, attribute_value = function_call[0]
        assert attribute_key == key
        assert re.match(re.compile(self.version_pattern), attribute_value)

    @patch('newrelic.agent')
    def test_record_python_and_django_version(self, mock_newrelic_agent):
        """
        Test that the DeploymentMonitoringMiddleware records the correct Python and Django versions
        """
        middleware = DeploymentMonitoringMiddleware(Mock())
        middleware(Mock())

        parameter_calls_count = mock_newrelic_agent.add_custom_parameter.call_count
        assert parameter_calls_count == 2

        function_calls = mock_newrelic_agent.add_custom_parameter.call_args_list
        self._test_key_value_pair(function_calls[0], 'python_version')
        self._test_key_value_pair(function_calls[1], 'django_version')
