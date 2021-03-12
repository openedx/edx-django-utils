""" """
from logging import getLogger

from .exceptions import HookException
from .pipeline import run_action_pipeline, run_filter_pipeline

log = getLogger(__name__)


def trigger_filter(trigger_name, *args, **kwargs):
    """
    Function that manages the filters pipeline.

    Arguments:
        trigger_name:


    Return:
        result:
    """
    try:
        result = run_filter_pipeline(trigger_name, *args, **kwargs)
    except HookException as exc:
        raise exc

    return result


def trigger_action(trigger_name, *args, **kwargs):
    """
    Function that manages the filters pipeline.

    Arguments:
        trigger_name:


    Return:
        result:
    """
    try:
        run_action_pipeline(trigger_name, *args, **kwargs)
    except HookException as exc:
        log.exception(
                "Failed running action pipeline, error: %s",
                exc,
        )
