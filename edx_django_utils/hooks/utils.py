"""
Utilities for the hooks module.
"""
from logging import getLogger

from django.conf import settings
from django.utils.module_loading import import_string

log = getLogger(__name__)


def get_functions_for_pipeline(pipeline):
    """
    Helper function that given a pipeline with functions paths gets the objects related
    to each path.

    Example usage:
        functions = get_functions_for_pipeline(['1st_path_to_function', ...])
        >>> functions
        [
            <function 1st_function at 0x00000000000>,
            <function 2nd_function at 0x00000000001>,
            ...
        ]

    Arguments:
        pipeline (list): paths where functions are defined.

    Returns:
        function_list (list): function objects defined in pipeline.
    """
    function_list = []
    for function_path in pipeline:
        try:
            function = import_string(function_path)
            function_list.append(function)
        except ImportError:
            log.exception("Failed to import '%s'.", function_path)

    return function_list


def get_pipeline_configuration(trigger_name):
    """
    Helper function used to get the configuration needed to execute the Pipeline Runner.
    It will take from the hooks configuration the ist of functions to execute and how to execute them.

    Example usage:
        pipeline_config = get_pipeline_configuration('trigger')
        >>> pipeline_config
            (
                [
                    'my_plugin.hooks.filters.test_function',
                    'my_plugin.hooks.filters.test_function_2nd',
                ],
            )

    Arguments:
        trigger_name (str): determines which is the trigger of this pipeline.

    Returns:
        pipeline (list): paths where functions for the pipeline are defined.
    """
    hook_config = get_hook_configurations(trigger_name)

    if not hook_config:
        return []

    pipeline = []

    if isinstance(hook_config, dict):
        pipeline = hook_config.get("pipeline", [])

    elif isinstance(hook_config, list):
        pipeline = hook_config

    elif isinstance(hook_config, str):
        pipeline.append(hook_config)

    return pipeline


def get_hook_configurations(trigger_name):
    """
    Helper function used to get configuration needed for using Hooks Extension Framework.

    Example usage:
            configuration = get_hook_configurations('trigger')
            >>> configuration
            {
                'pipeline':
                    [
                        'my_plugin.hooks.filters.test_function',
                        'my_plugin.hooks.filters.test_function_2nd',
                    ],
            }

    Arguments:
        trigger_name (str): determines which configuration to use.

    Returns:
        hooks configuration (dict): taken from Django settings containing hooks configuration.
    """
    hooks_config = getattr(settings, "HOOKS_EXTENSION_CONFIG", {})

    return hooks_config.get(trigger_name, {})
