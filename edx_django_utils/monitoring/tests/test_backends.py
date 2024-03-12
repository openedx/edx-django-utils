"""
Tests for TelemetryBackend and implementations.
"""
from unittest.mock import patch

import ddt
from django.test import TestCase, override_settings

from edx_django_utils.monitoring.internal.backends import TelemetryBackend, configured_backends


class TestingBackend(TelemetryBackend):
    """
    A dummy backend to use in addition to the NR backend, and instead
    of the OTel and DD backends (which can't be loaded due to missing
    dependencies.)
    """
    def set_attribute(self, key, value):
        pass

    def record_exception(self):
        pass


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
            ['edx_django_utils.monitoring.tests.test_backends.TestingBackend'],
            ['TestingBackend']
        ),
        # Several known classes
        (
            [
                'edx_django_utils.monitoring.tests.test_backends.TestingBackend',
                'edx_django_utils.monitoring.NewRelicBackend'
            ],
            ['TestingBackend', 'NewRelicBackend']
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

    @patch('edx_django_utils.monitoring.internal.backends.log')
    def test_import_failure(self, mock_log):
        """
        Test that backends that can't be imported are ignored, with warning.
        """
        with override_settings(OPENEDX_TELEMETRY=[
                'nonsense',
                'edx_django_utils.monitoring.tests.test_backends.TestingBackend',
        ]):
            assert self._get_configured_classnames() == ['TestingBackend']
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
                'edx_django_utils.monitoring.tests.test_backends.TestingBackend',
        ]):
            assert self._get_configured_classnames() == ['TestingBackend']
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
        assert [b.__class__.__name__ for b in configured_backends()] == ['NewRelicBackend']
