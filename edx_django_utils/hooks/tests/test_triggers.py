"""
Tests for `edx-django-utils` hooks triggers.
"""
from unittest.mock import Mock, patch

from django.test import TestCase

from ..triggers import trigger_filter


class TestTriggerFilter(TestCase):
    """
    Test class to verify standard behavior of trigger_filter.
    """

    def setUp(self):
        """
        Setup common conditions for every test case.
        """
        super().setUp()
        self.kwargs = {
            "request": Mock(),
        }

    @patch("edx_django_utils.hooks.triggers.run_pipeline")
    @patch("edx_django_utils.hooks.triggers.get_pipeline_configuration")
    def test_run_empty_pipeline(self, get_configuration_mock, run_pipeline_mock):
        """
        This method runs trigget_filter with an empty pipeline.

        Expected behavior:
            Returns keyword arguments without calling the pipeline runner.
        """
        get_configuration_mock.return_value = []

        result = trigger_filter("trigger_name", **self.kwargs)

        self.assertDictEqual(result, self.kwargs)
        run_pipeline_mock.assert_not_called()

    @patch("edx_django_utils.hooks.triggers.run_pipeline")
    @patch("edx_django_utils.hooks.triggers.get_pipeline_configuration")
    def test_affecting_execution(self, get_configuration_mock, run_pipeline_mock):
        """
        This method runs trigget_filter affecting the application flow raising exceptions.

        Expected behavior:
            Run pipeline is called with raise_exception equals to True.
            Also, given that by default filters are synchronous, then get_pipeline_configuration is
            called with async_default equals to False.
        """
        pipeline = Mock()
        get_configuration_mock.return_value = pipeline

        trigger_filter("trigger_name", **self.kwargs)

        get_configuration_mock.assert_called_once_with("trigger_name")
        run_pipeline_mock.assert_called_once_with(
            pipeline, raise_exception=True, **self.kwargs
        )
