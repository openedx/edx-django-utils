"""
Tests monitoring middleware.

Note: CachedCustomMonitoringMiddleware is tested in ``test_monitoring.py``.
"""
from unittest.mock import patch

from django.test import TestCase
from django.test.client import RequestFactory
from waffle.testutils import override_switch

from edx_django_utils.monitoring import MonitoringMemoryMiddleware


class TestMonitoringMemoryMiddleware(TestCase):
    """
    Tests for MonitoringMemoryMiddleware
    """
    @override_switch('edx_django_utils.monitoring.enable_memory_middleware', False)
    @patch('edx_django_utils.monitoring.internal.middleware.log')
    def test_memory_monitoring_when_disabled(self, mock_logger):
        MonitoringMemoryMiddleware().process_response(
            'fake request',
            'fake response',
        )
        mock_logger.info.assert_not_called()

    @override_switch('edx_django_utils.monitoring.enable_memory_middleware', True)
    @patch('edx_django_utils.monitoring.internal.middleware.log')
    def test_memory_monitoring_when_enabled(self, mock_logger):
        request = RequestFactory().get('/')
        MonitoringMemoryMiddleware().process_response(
            request,
            'fake response',
        )
        mock_logger.info.assert_called()
