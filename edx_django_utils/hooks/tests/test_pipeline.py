"""
Tests for `edx-django-utils` hooks pipeline.
"""
from unittest.mock import Mock, patch

from django.test import TestCase

from ..exceptions import HookException
from ..pipeline import run_pipeline


class TestRunningPipeline(TestCase):
    """
    Test class to verify standard behavior of the Pipeline runner.
    """

    def setUp(self):
        """
        Setup common conditions for every test case.
        """
        super().setUp()
        self.kwargs = {
            "request": Mock(),
        }
        self.pipeline = Mock()

    @patch("edx_django_utils.hooks.pipeline.get_functions_for_pipeline")
    def test_run_empty_pipeline(self, get_functions_mock):
        """
        This method runs an empty pipeline, i.e, a pipeline without defined functions.

        Expected behavior:
            Returns the same input arguments.
        """
        get_functions_mock.return_value = []

        result = run_pipeline([], **self.kwargs)

        get_functions_mock.assert_called_once_with([])
        self.assertEqual(result, self.kwargs)

    @patch("edx_django_utils.hooks.pipeline.get_functions_for_pipeline")
    def test_raise_hook_exception(self, get_functions_mock):
        """
        This method runs a pipeline with a function that raises HookException.

        Expected behavior:
            The pipeline re-raises the exception caught.
        """
        exception_message = "There was an error executing filter X."
        function = Mock(side_effect=HookException(message=exception_message))
        function.__name__ = "function_name"
        get_functions_mock.return_value = [function]
        log_message = "Exception raised while running '{func_name}':\n HookException: {exc_msg}".format(
            func_name="function_name", exc_msg=exception_message,
        )

        with self.assertRaises(HookException), self.assertLogs() as captured:
            run_pipeline(self.pipeline, raise_exception=True, **self.kwargs)
        self.assertEqual(
            captured.records[0].getMessage(), log_message,
        )

    @patch("edx_django_utils.hooks.pipeline.get_functions_for_pipeline")
    def test_not_raise_hook_exception(self, get_functions_mock):
        """
        This method runs a pipeline with a function that raises HookException but
        raise_exception is set to False.

        Expected behavior:
            The pipeline does not re-raise the exception caught.
        """
        return_value = {
            "request": Mock(),
        }
        function_with_exception = Mock(side_effect=HookException)
        function_without_exception = Mock(return_value=return_value)
        get_functions_mock.return_value = [
            function_with_exception,
            function_without_exception,
        ]

        result = run_pipeline(self.pipeline, **self.kwargs)

        self.assertEqual(result, return_value)
        function_without_exception.assert_called_once_with(**self.kwargs)

    @patch("edx_django_utils.hooks.pipeline.get_functions_for_pipeline")
    def test_not_raise_common_exception(self, get_functions_mock):
        """
        This method runs a pipeline with a function that raises a common Exception.

        Expected behavior:
            The pipeline continues execution after caughting Exception.
        """
        return_value = {
            "request": Mock(),
        }
        function_with_exception = Mock(side_effect=ValueError("Value error exception"))
        function_with_exception.__name__ = "function_with_exception"
        function_without_exception = Mock(return_value=return_value)
        get_functions_mock.return_value = [
            function_with_exception,
            function_without_exception,
        ]
        log_message = (
            "Exception raised while running 'function_with_exception': Value error exception\n"
            "Continuing execution."
        )

        with self.assertLogs() as captured:
            result = run_pipeline(self.pipeline, **self.kwargs)

        self.assertEqual(
            captured.records[0].getMessage(), log_message,
        )
        self.assertEqual(result, return_value)
        function_without_exception.assert_called_once_with(**self.kwargs)

    @patch("edx_django_utils.hooks.pipeline.get_functions_for_pipeline")
    def test_getting_pipeline_result(self, get_functions_mock):
        """
        This method runs a pipeline with functions defined via configuration.

        Expected behavior:
            Returns the processed dictionary.
        """
        return_value_1st = {
            "request": Mock(),
        }
        return_value_2nd = {
            "user": Mock(),
        }
        return_overall_value = {**return_value_1st, **return_value_2nd}
        first_function = Mock(return_value=return_value_1st)
        second_function = Mock(return_value=return_value_2nd)
        get_functions_mock.return_value = [
            first_function,
            second_function,
        ]

        result = run_pipeline(self.pipeline, **self.kwargs)

        first_function.assert_called_once_with(**self.kwargs)
        second_function.assert_called_once_with(**return_value_1st)
        self.assertDictEqual(result, return_overall_value)

    @patch("edx_django_utils.hooks.pipeline.get_functions_for_pipeline")
    def test_partial_pipeline(self, get_functions_mock):
        """
        This method runs a pipeline with functions defined via configuration.
        At some point, returns an object to stop execution.

        Expected behavior:
            Returns the object used to stop execution.
        """
        return_value_1st = Mock()
        first_function = Mock(return_value=return_value_1st)
        first_function.__name__ = "first_function"
        second_function = Mock()
        get_functions_mock.return_value = [
            first_function,
            second_function,
        ]
        log_message = "Pipeline stopped by 'first_function' for returning an object."

        with self.assertLogs() as captured:
            result = run_pipeline(self.pipeline, **self.kwargs)

        self.assertEqual(
            captured.records[0].getMessage(), log_message,
        )
        first_function.assert_called_once_with(**self.kwargs)
        second_function.assert_not_called()
        self.assertEqual(result, return_value_1st)
