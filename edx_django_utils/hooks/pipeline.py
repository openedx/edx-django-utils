"""
Pipeline runner used to execute list of functions (actions or filters).
"""
from logging import getLogger

from .exceptions import HookException
from .utils import get_functions_for_pipeline

log = getLogger(__name__)


def run_pipeline(pipeline, *args, raise_exception=False, **kwargs):
    """
    Given a list of functions paths, this function  will execute them using the Accumulative Pipeline
    pattern defined in docs/decisions/0006-hooks-tooling-pipeline.rst

    Example usage:
        result = run_pipeline(
            [
                'my_plugin.hooks.filters.test_function',
                'my_plugin.hooks.filters.test_function_2nd'
            ],
            raise_exception=True,
            request=request,
            user=user,
        )
        >>> result
       {
           'result_test_function': Object,
           'result_test_function_2nd': Object_2nd,
       }

    Arguments:
        pipeline (list): paths where each function is defined.

    Keyword arguments:
        raise_exception (bool): used to determine whether the pipeline will raise HookExceptions. Default is set
        to False.

    Returns:
        out (dict): accumulated outputs of the functions defined in pipeline.
        result (obj): return object of one of the pipeline functions. This will be the return object for the pipeline
        if one of the functions returns an object different than Dict o None.

    Exceptions raised:
        HookException: custom exception re-raised when a function raised an exception of
        this type and raise_exception is set to True. This behavior is common when using filters.

    This pipeline implementation was inspired by: Social auth core. For more information check their Github
    repository: https://github.com/python-social-auth/social-core
    """
    functions = get_functions_for_pipeline(pipeline)

    out = kwargs.copy()
    for function in functions:
        try:
            result = function(*args, **out) or {}
            if not isinstance(result, dict):
                log.info(
                    "Pipeline stopped by '%s' for returning an object.",
                    function.__name__,
                )
                return result
            out.update(result)
        except HookException as exc:
            if raise_exception:
                log.exception(
                    "Exception raised while running '%s':\n %s", function.__name__, exc,
                )
                raise exc
        except Exception as exc:  # pylint: disable=broad-except
            # We're catching this because we don't want the core to blow up when a
            # hook is broken. This exception will probably need some sort of
            # monitoring hooked up to it to make sure that these errors don't go
            # unseen.
            log.exception(
                "Exception raised while running '%s': %s\n%s",
                function.__name__,
                exc,
                "Continuing execution.",
            )
            continue

    return out
