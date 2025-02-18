"""
Tests monitoring utils.
"""
from unittest.mock import patch

from django.test import TestCase, override_settings

from edx_django_utils.monitoring import monitor_django_management_command


class MonitorDjangoManagementCommandTests(TestCase):
    """Test suite for monitor_django_management_command."""

    @patch("edx_django_utils.monitoring.internal.utils.function_trace")
    @patch("edx_django_utils.monitoring.internal.utils.set_monitoring_transaction_name")
    def test_monitoring_enabled(self, mock_set_transaction_name, mock_function_trace):
        """
        Test that when custom management command monitoring is enabled:
        - function_trace is called with the correct trace name.
        - set_monitoring_transaction_name is called with the correct command name.
        """

        with override_settings(ENABLE_CUSTOM_MANAGEMENT_COMMAND_MONITORING=True):
            with monitor_django_management_command("test_command"):
                pass

            mock_function_trace.assert_called_once_with("django.command")
            mock_set_transaction_name.assert_called_once_with("test_command")

    @patch("edx_django_utils.monitoring.internal.utils.function_trace")
    @patch("edx_django_utils.monitoring.internal.utils.set_monitoring_transaction_name")
    def test_monitoring_disabled(self, mock_set_transaction_name, mock_function_trace):
        """
        Test that when custom management command monitoring is disabled:
        - function_trace and set_monitoring_transaction_name are not called.
        """

        with override_settings(ENABLE_CUSTOM_MANAGEMENT_COMMAND_MONITORING=False):
            with monitor_django_management_command("test_command"):
                pass

            mock_function_trace.assert_not_called()
            mock_set_transaction_name.assert_not_called()

    @patch("edx_django_utils.monitoring.internal.utils.function_trace")
    @patch("edx_django_utils.monitoring.internal.utils.set_monitoring_transaction_name")
    def test_custom_trace_name_usage(self, mock_set_name, mock_function_trace):
        """
        Test that a custom trace name is used when DJANGO_MANAGEMENT_MONITORING_FUNCTION_TRACE_NAME
        is explicitly set.
        """

        with override_settings(
            ENABLE_CUSTOM_MANAGEMENT_COMMAND_MONITORING=True,
            DJANGO_MANAGEMENT_MONITORING_FUNCTION_TRACE_NAME="custom.trace",
        ):
            with monitor_django_management_command("test_command"):
                pass

            mock_function_trace.assert_called_once_with("custom.trace")
            mock_set_name.assert_called_once_with("test_command")
