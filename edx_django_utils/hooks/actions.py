"""
Hooks actions functions.

Please remember to expose any new public methods in the `__init__.py` file.
"""
from logging import getLogger

from django.conf import settings
from .utils import get_cached_functions_for_hook

log = getLogger(__name__)


def do_action(trigger_name, *args, **kwargs):
    """
    Will check in the django setting HOOKS_EXTENSIONS the trigger_name key and call their configured
    functions.

    Params:
        trigger_name: a string that determines which is the trigger of this action.
    """

    action_functions, are_async = get_cached_functions_for_hook(trigger_name)
    for action_function in action_functions:
        try:
            action_function(*args, **kwargs)
        except Exception as exc:  # pylint: disable=broad-except
            # We're catching this because we don't want the core to blow up when a
            # hook is broken. This exception will probably need some sort of
            # monitoring hooked up to it to make sure that these errors don't go
            # unseen.
            log.exception(
                "Failed to call action function. Error: %s",
                exc,
            )
            continue
