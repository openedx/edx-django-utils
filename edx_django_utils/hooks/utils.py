""" Utilities for the hooks module. """
from logging import getLogger

from importlib import import_module
from django.conf import settings

log = getLogger(__name__)


# TODO: add cache decorator
def get_cached_functions_for_hook(trigger_name):
    """
    Returns a tuple where the first item is the functions associated with the trigger and the second
    item is a boolean that indicates wheter they should be run in an async way or not.

    NOTE: These will be functions will be cached (in RAM not memcache) on this unique
    combination. If we enable many new hooks to use this system, we may notice an
    increase in memory usage as the entirety of these functions will be held in memory.
    """
    hook_config = _get_hook_configurations(trigger_name)

    hook_is_async = hook_config.get("async", True)

    hook_functions = []
    for action_function_path in hook_config.get("pipeline", []):
        module_path, _, name = action_function_path.rpartition(".")
        try:
            module = import_module(module_path)
            hook_function = getattr(module, name)
            hook_functions.append(hook_function)
        except ImportError:
            log.exception(
                "Failed to import %s module when creating %s action",
                module_path,
                trigger_name,
            )
        except AttributeError:
            log.warning(
                "Failed to retrieve %s function when creating %s action",
                name,
                module_path,
                trigger_name,
            )

    return hook_functions, hook_is_async


def _get_hook_configurations(trigger_name):
    """ TODO: add me"""
    hooks_config = getattr(settings, "HOOKS_EXTENSIONS", {})  # TODO: change this to HOOKS_CONFIG

    return hooks_config.get(trigger_name, {})
