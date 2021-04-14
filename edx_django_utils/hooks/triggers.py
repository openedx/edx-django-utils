"""
Triggers for actions and filters.
"""
from .pipeline import run_pipeline
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
    pipeline = get_pipeline_configuration(trigger_name)

    if not pipeline:
        return kwargs

    return run_pipeline(pipeline, *args, raise_exception=True, **kwargs)
