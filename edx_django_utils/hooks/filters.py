"""
Hooks filter functions

Please remember to expose any new public methods in the `__init__.py` file.
"""
from logging import getLogger

from django.conf import settings
from .utils import get_cached_functions_for_hook
from .exceptions import HookException

log = getLogger(__name__)


def do_filter(trigger_name, *args, **kwargs):
    """
    Will check in the django setting HOOKS_EXTENSIONS the trigger_name key and call their configured
    functions.

    Params:
        trigger_name: a string that determines which is the trigger of this filter.
    """

    filter_functions, are_async = get_cached_functions_for_hook(trigger_name)
    out = kwargs.copy()
    for filter_function in filter_functions:
        try:
            result = filter_function(*args, **out) or {}
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
