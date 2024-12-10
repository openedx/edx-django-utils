"""
Tests for TelemetryBackend and implementations.
"""
from unittest.mock import patch

import ddt
import pytest
from django.test import TestCase, override_settings

from edx_django_utils.monitoring import record_exception, set_custom_attribute
from edx_django_utils.monitoring.internal.backends import configured_backends


@ddt.ddt
class TestBackendsConfig(TestCase):
    """
    Test configuration of the backends list.
    """

    def _get_configured_classnames(self):
        return [b.__class__.__name__ for b in configured_backends()]

    @ddt.data(
        # Default
        (None, ['NewRelicBackend']),
        # Empty list removes all
        ([], []),
        # New Relic not required
        (
            ['edx_django_utils.monitoring.OpenTelemetryBackend'],
            ['OpenTelemetryBackend']
        ),
        # All known classes
        (
            [
                'edx_django_utils.monitoring.NewRelicBackend',
                'edx_django_utils.monitoring.OpenTelemetryBackend',
                'edx_django_utils.monitoring.DatadogBackend',
            ],
            ['NewRelicBackend', 'OpenTelemetryBackend', 'DatadogBackend'],
        ),
    )
    @ddt.unpack
    def test_configured_backends(self, setting, expected_classnames):
        """
        Test that backends are loaded as expected.
        """
        with override_settings(OPENEDX_TELEMETRY=setting):
            backend_classnames = self._get_configured_classnames()
            assert sorted(backend_classnames) == sorted(expected_classnames)

    def test_type(self):
        """
        Test that we detect the misuse of a string instead of a list.
        """
        with override_settings(OPENEDX_TELEMETRY='edx_django_utils.monitoring.NewRelicBackend'):
            with pytest.raises(Exception, match='must be a list, not a string'):
                self._get_configured_classnames()

    @patch('edx_django_utils.monitoring.internal.backends.log')
    def test_import_failure(self, mock_log):
        """
        Test that backends that can't be imported are ignored, with warning.
        """
        with override_settings(OPENEDX_TELEMETRY=[
                'nonsense',
                'edx_django_utils.monitoring.OpenTelemetryBackend',
        ]):
            assert self._get_configured_classnames() == ['OpenTelemetryBackend']
        mock_log.warning.assert_called_once_with(
            "Could not load OPENEDX_TELEMETRY option 'nonsense': "
            """ImportError("nonsense doesn't look like a module path")"""
        )

    @patch('edx_django_utils.monitoring.internal.backends.log')
    def test_wrong_class(self, mock_log):
        """
        Test that backend classes of an unexpected ancestor are ignored, with warning.
        """
        with override_settings(OPENEDX_TELEMETRY=[
                'builtins.dict',
                'edx_django_utils.monitoring.OpenTelemetryBackend',
        ]):
            assert self._get_configured_classnames() == ['OpenTelemetryBackend']
        mock_log.warning.assert_called_once_with(
            "Could not load OPENEDX_TELEMETRY option 'builtins.dict': "
            "<class 'dict'> is not a subclass of TelemetryBackend"
        )

    @patch('edx_django_utils.monitoring.internal.backends.log')
    @patch('edx_django_utils.monitoring.internal.backends.newrelic', None)
    def test_newrelic_package(self, mock_log):
        """
        Test that New Relic backend is skipped if package not present.
        """
        with override_settings(OPENEDX_TELEMETRY=['edx_django_utils.monitoring.NewRelicBackend']):
            assert self._get_configured_classnames() == []
        mock_log.warning.assert_called_once_with(
            "Could not load OPENEDX_TELEMETRY option 'edx_django_utils.monitoring.NewRelicBackend': "
            "Exception('Could not load New Relic monitoring backend; package not present.')"
        )

    def test_default_config(self):
        """
        We need to keep the same unconfigured default for now.
        """
        assert [b.__class__.__name__ for b in configured_backends()] == ['NewRelicBackend']


class TestBackendsFanOut(TestCase):
    """
    Test that certain utility functions fan out to the backends.
    """

    @patch('newrelic.agent.add_custom_parameter')
    @patch('opentelemetry.trace.span.NonRecordingSpan.set_attribute')
    # Patch out the span-getter, not the set_attribute call, because
    # it doesn't give us a span unless one is active. And I didn't
    # feel like setting that up.
    #
    # This does at least assert that we're getting the *root* span for DD.
    @patch('ddtrace._trace.tracer.Tracer.current_root_span')
    def test_set_custom_attribute(
            self, mock_dd_root_span,
            mock_otel_set_attribute, mock_nr_add_custom_parameter,
    ):
        with override_settings(OPENEDX_TELEMETRY=[
                'edx_django_utils.monitoring.NewRelicBackend',
                'edx_django_utils.monitoring.OpenTelemetryBackend',
                'edx_django_utils.monitoring.DatadogBackend',
        ]):
            set_custom_attribute('some_key', 'some_value')
        mock_nr_add_custom_parameter.assert_called_once_with('some_key', 'some_value')
        mock_otel_set_attribute.assert_called_once()
        mock_dd_root_span.assert_called_once()

    @patch('newrelic.agent.record_exception')
    @patch('opentelemetry.trace.span.NonRecordingSpan.record_exception')
    # Record exception on current span, not root span.
    @patch('ddtrace._trace.tracer.Tracer.current_span')
    def test_record_exception(
            self, mock_dd_span,
            mock_otel_record_exception, mock_nr_record_exception,
    ):
        with override_settings(OPENEDX_TELEMETRY=[
                'edx_django_utils.monitoring.NewRelicBackend',
                'edx_django_utils.monitoring.OpenTelemetryBackend',
                'edx_django_utils.monitoring.DatadogBackend',
        ]):
            record_exception()
        mock_nr_record_exception.assert_called_once()
        mock_otel_record_exception.assert_called_once()
        mock_dd_span.assert_called_once()
