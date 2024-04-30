"""
Tests for utilities in monitoring.
"""

from unittest.mock import patch

from edx_django_utils.monitoring import background_task


@patch('edx_django_utils.monitoring.internal.utils.newrelic')
def test_background_task_wrapper(wrapped_nr):
    # We are verifying that this returns the correct decorated function
    # in the two cases we care about.
    returned_func = background_task()

    assert returned_func == wrapped_nr.agent.background_task()


@patch('edx_django_utils.monitoring.internal.utils.newrelic', None)
def test_background_task_wrapper_no_new_relic():
    # Test that the decorator behaves as a no-op when newrelic is not set.
    returned_func = background_task()
    wrapped_value = returned_func('a')

    assert wrapped_value == 'a'
