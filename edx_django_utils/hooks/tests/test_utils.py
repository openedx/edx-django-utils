"""
Tests for the `edx-django-utils` hooks utilities.
"""
from unittest.mock import patch

import ddt
from django.test import TestCase, override_settings

from ..utils import get_functions_for_pipeline, get_hook_configurations, get_pipeline_configuration


def test_function():
    """
    Utility function used when getting functions for pipeline.
    """


@ddt.ddt
class TestUtilityFunctions(TestCase):
    """
    Test class to verify standard behavior of hooks utility functions.
    """

    def test_get_empty_function_list(self):
        """
        This method is used to verify the behavior of get_functions_for_pipeline
        when an empty pipeline is passed as argument.

        Expected behavior:
            Returns an empty list.
        """
        pipeline = []

        function_list = get_functions_for_pipeline(pipeline)

        self.assertEqual(function_list, pipeline)

    def test_get_non_existing_function(self):
        """
        This method is used to verify the behavior of get_functions_for_pipeline
        when a non-existing function path is passed inside the pipeline argument.

        Expected behavior:
            Returns a list without the non-existing function.
        """
        pipeline = [
            "edx_django_utils.hooks.tests.test_utils.test_function",
            "edx_django_utils.hooks.tests.test_utils.non_existent",
        ]
        log_message = "Failed to import '{}'.".format(
            "edx_django_utils.hooks.tests.test_utils.non_existent"
        )

        with self.assertLogs() as captured:
            function_list = get_functions_for_pipeline(pipeline)

        self.assertEqual(
            captured.records[0].getMessage(), log_message,
        )
        self.assertEqual(function_list, [test_function])

    def test_get_non_existing_module_func(self):
        """
        This method is used to verify the behavior of get_functions_for_pipeline
        when a non-existing module path is passed inside the pipeline argument.

        Expected behavior:
            Returns a list without the non-existing function.
        """
        pipeline = [
            "edx_django_utils.hooks.tests.test_utils.test_function",
            "edx_django_utils.hooks.non_existent.test_utils.test_function",
        ]
        log_message = "Failed to import '{}'.".format(
            "edx_django_utils.hooks.non_existent.test_utils.test_function"
        )

        with self.assertLogs() as captured:
            function_list = get_functions_for_pipeline(pipeline)

        self.assertEqual(captured.records[0].getMessage(), log_message)
        self.assertEqual(function_list, [test_function])

    def test_get_function_list(self):
        """
        This method is used to verify the behavior of get_functions_for_pipeline
        when a list of functions paths is passed as the pipeline parameter.

        Expected behavior:
            Returns a list with the function objects.
        """
        pipeline = [
            "edx_django_utils.hooks.tests.test_utils.test_function",
            "edx_django_utils.hooks.tests.test_utils.test_function",
        ]

        function_list = get_functions_for_pipeline(pipeline)

        self.assertEqual(function_list, [test_function] * 2)

    def test_get_empty_hook_config(self):
        """
        This method is used to verify the behavior of get_hook_configurations
        when a trigger without a HOOKS_EXTENSION_CONFIG is passed as parameter.

        Expected behavior:
            Returns an empty dictionary.
        """
        result = get_hook_configurations("trigger_name")

        self.assertEqual(result, {})

    @override_settings(
        HOOKS_EXTENSION_CONFIG={
            "trigger_name": {
                "pipeline": [
                    "edx_django_utils.hooks.tests.test_utils.test_function",
                    "edx_django_utils.hooks.tests.test_utils.test_function",
                ],
                "async": False,
            }
        }
    )
    def test_get_hook_config(self):
        """
        This method is used to verify the behavior of get_hook_configurations
        when a trigger with HOOKS_EXTENSION_CONFIG defined is passed as parameter.

        Expected behavior:
            Returns a tuple with pipeline configurations.
        """
        expected_result = {
            "pipeline": [
                "edx_django_utils.hooks.tests.test_utils.test_function",
                "edx_django_utils.hooks.tests.test_utils.test_function",
            ],
            "async": False,
        }

        result = get_hook_configurations("trigger_name")

        self.assertDictEqual(result, expected_result)

    @patch("edx_django_utils.hooks.utils.get_hook_configurations")
    @ddt.data(
        (("edx_django_utils.hooks.tests.test_utils.test_function",), []),
        ({}, []),
        (
            {
                "pipeline": [
                    "edx_django_utils.hooks.tests.test_utils.test_function",
                    "edx_django_utils.hooks.tests.test_utils.test_function",
                ],
            },
            [
                "edx_django_utils.hooks.tests.test_utils.test_function",
                "edx_django_utils.hooks.tests.test_utils.test_function",
            ],
        ),
        (
            [
                "edx_django_utils.hooks.tests.test_utils.test_function",
                "edx_django_utils.hooks.tests.test_utils.test_function",
            ],
            [
                "edx_django_utils.hooks.tests.test_utils.test_function",
                "edx_django_utils.hooks.tests.test_utils.test_function",
            ],
        ),
        (
            "edx_django_utils.hooks.tests.test_utils.test_function",
            ["edx_django_utils.hooks.tests.test_utils.test_function", ],
        ),
    )
    @ddt.unpack
    def test_get_pipeline_config(self, config, expected_result, get_config_mock):
        """
        This method is used to verify the behavior of get_pipeline_configuration
        when a trigger with HOOKS_EXTENSION_CONFIG defined is passed as parameter.

        Expected behavior:
            Returns a tuple with the pipeline and synchronous configuration.
        """
        get_config_mock.return_value = config

        result = get_pipeline_configuration("trigger_name")

        self.assertListEqual(result, expected_result)
