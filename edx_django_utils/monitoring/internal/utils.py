"""
Defines several custom monitoring helpers, some of which work with
the CachedCustomMonitoringMiddleware.

Usage:

    from edx_django_utils.monitoring import accumulate
    ...
    accumulate('xb_user_state.get_many.num_items', 4)

There is no need to do anything else.  The custom attributes are automatically
cleared before the next request.

We try to keep track of our custom monitoring at:
https://openedx.atlassian.net/wiki/spaces/PERF/pages/54362736/Custom+Attributes+in+New+Relic

At this time, the custom monitoring will only be reported to New Relic.

"""
from contextlib import ExitStack, contextmanager

from .backends import configured_backends
from .middleware import CachedCustomMonitoringMiddleware

try:
    import newrelic.agent
except ImportError:  # pragma: no cover
    newrelic = None  # pylint: disable=invalid-name


def accumulate(name, value):
    """
    Accumulate monitoring custom attribute for the current request.

    The named attribute is accumulated by a numerical amount using the sum.  All
    attributes are queued up in the request_cache for this request.  At the end of
    the request, the monitoring_utils middleware will batch report all
    queued accumulated attributes to the monitoring tool (e.g. New Relic).

    Arguments:
        name (str): The attribute name.  It should be period-delimited, and
            increase in specificity from left to right.  For example:
            'xb_user_state.get_many.num_items'.
        value (number):  The amount to accumulate into the named attribute.  When
            accumulate() is called multiple times for a given attribute name
            during a request, the sum of the values for each call is reported
            for that attribute.  For attributes which don't make sense to accumulate,
            use ``set_custom_attribute`` instead.

    """
    CachedCustomMonitoringMiddleware.accumulate_attribute(name, value)


def increment(name):
    """
    Increment a monitoring custom attribute representing a counter.

    Here we simply accumulate a new custom attribute with a value of 1, and the
    middleware should automatically aggregate this attribute.
    """
    accumulate(name, 1)


def set_custom_attributes_for_course_key(course_key):
    """
    Set monitoring custom attributes related to a course key.

    This is not cached.

    """
    set_custom_attribute('course_id', str(course_key))
    set_custom_attribute('org', str(course_key.org))


def set_custom_attribute(key, value):
    """
    Set monitoring custom attribute.

    This is not cached.
    """
    for backend in configured_backends():
        backend.set_attribute(key, value)


def record_exception():
    """
    Record a caught exception to the monitoring system.

    Note: By default, only unhandled exceptions are monitored. This function
    can be called to record exceptions as monitored errors, even if you handle
    the exception gracefully from a user perspective.
    """
    for backend in configured_backends():
        backend.record_exception()


@contextmanager
def function_trace(function_name):
    """
    Wraps a chunk of code that we want to appear as a separate, explicit,
    segment in our monitoring tools.
    """
    # Not covering this because if we mock it, we're not really testing anything
    # anyway. If something did break, it should show up in tests for apps that
    # use this code with whatever uses it.
    # ExitStack handles the underlying context managers.
    with ExitStack() as stack:
        for backend in configured_backends():
            context = backend.create_span(function_name)
            if context is not None:
                stack.enter_context(context)
        yield


def background_task(*args, **kwargs):
    """
    Handles monitoring for background tasks that are not passed in through the web server like
    celery and event consuming tasks.

    This function only supports New Relic.

    For more details, see:
    https://docs.newrelic.com/docs/apm/agents/python-agent/python-agent-api/backgroundtask-python-agent-api/

    """
    def noop_decorator(func):
        return func

    if newrelic:  # pragma: no cover
        return newrelic.agent.background_task(*args, **kwargs)
    else:
        return noop_decorator
