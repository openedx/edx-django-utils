"""
Triggers for actions and filters.
"""
from .tasks import run_pipeline
from .utils import get_pipeline_configuration


def trigger_filter(trigger_name, *args, **kwargs):
    """
    Function that manages the execution of filters listening on a trigger. The execution
    follows the Pipeline pattern using the pipeline runner.

    Example usage:
        result = trigger_filter(
            'trigger_name_used_in_hooks_config',
            request,
            user=user,
        )
        >>> result
       {
           'result_test_function': Object,
           'result_test_function_2nd': Object_2nd,
       }

    Arguments:
        trigger_name (str): determines which trigger we are listening to. It also specifies which
        hook configuration to use when calling trigger_filter.

    Returns:
        result (dict): result of the pipeline execution, i.e the accumulated output of the filters defined in
        the hooks configuration.
    """
    pipeline, is_async = get_pipeline_configuration(trigger_name)

    if not pipeline:
        return kwargs

    if is_async:
        result = run_pipeline(
            pipeline, *args, raise_exception=True, **kwargs
        )  # TODO: change to async call.
    else:
        result = run_pipeline(pipeline, *args, raise_exception=True, **kwargs)

    return result


def trigger_action(trigger_name, *args, **kwargs):
    """
    Function that manages the execution of actions listening on a trigger action. The execution
    follows the Pipeline pattern using the pipeline runner.

    Example usage:
        trigger_action(
            'trigger_name_used_in_hooks_config',
            course_mode,
            user=user,
        )

    Arguments:
        trigger_name (str): determines which trigger we are listening to. It also specifies which
        hook configuration to use when calling trigger_action.

    Returns:
        None. By definition actions don't return any value.
    """
    pipeline, is_async = get_pipeline_configuration(trigger_name, async_default=True)

    if not pipeline:
        return

    if is_async:
        run_pipeline.delay(pipeline, *args, **kwargs)
    else:
        run_pipeline(pipeline, *args, **kwargs)
