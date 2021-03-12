"""
TODO: add description
"""
from logging import getLogger

from .exceptions import HookException
from .utils import get_cached_functions_for_hook

log = getLogger(__name__)


def run_pipeline(triggers, *args, **kwargs):
    """
    Will check in the django setting HOOKS_EXTENSIONS the trigger_name key and call their configured
    functions.
    Params:
        trigger_name: a string that determines which is the trigger of this filter.
    """
    out = kwargs.copy()
    for trigger in triggers:
        try:
            result = trigger(*args, **out) or {}
            if not isinstance(result, dict):
                return result
            out.update(result)
        except HookException as exc:
            raise exc
        except Exception as exc:  # pylint: disable=broad-except
            # We're catching this because we don't want the core to blow up when a
            # hook is broken. This exception will probably need some sort of
            # monitoring hooked up to it to make sure that these errors don't go
            # unseen.
            log.exception(
                "Failed to call action filter. Error: %s",
                exc,
            )
            continue

    return out


def run_filter_pipeline(trigger_name, *args, **kwargs):
    """
    Function that manages the filters pipeline.

    Arguments:
        trigger_name:


    Return:
        result:
    """
    triggers, is_async = get_cached_functions_for_hook(trigger_name)
    result = None

    if is_async:
        result = run_pipeline(triggers, *args, **kwargs)  # TODO: change to async call.
    else:
        result = run_pipeline(triggers, *args, **kwargs)

    return result


def run_action_pipeline(trigger_name, *args, **kwargs):
    """
    Function that manages the filters pipeline.

    Arguments:
        trigger_name:


    Return:
        None:
    """
    triggers, is_async = get_cached_functions_for_hook(trigger_name)

    if is_async:
        run_pipeline(triggers, *args, **kwargs)  # TODO: change to async call.
    else:
        run_pipeline(triggers, *args, **kwargs)
