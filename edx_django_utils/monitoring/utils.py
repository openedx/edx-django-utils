"""
This is an interface to the monitoring_utils middleware.  Functions
defined in this module can be used for custom monitoring.

Usage:

    from edx_django_utils import monitoring as monitoring_utils
    ...
    monitoring_utils.accumulate('xb_user_state.get_many.num_items', 4)

There is no need to do anything else.  The custom attributes are automatically
cleared before the next request.

We try to keep track of our custom monitoring at:

TODO: ARCHBOM-1490: Update to Custom Monitoring
https://openedx.atlassian.net/wiki/display/PERF/Custom+Metrics+in+New+Relic

At this time, the custom monitoring will only be reported to New Relic.

Please remember to expose any new methods in the `__init__.py` file.
"""
import warnings

from . import middleware

try:
    import newrelic.agent
except ImportError:
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
    middleware.CachedCustomMonitoringMiddleware.accumulate_attribute(name, value)


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

    This is not cached, and only support reporting to New Relic Insights.

    """
    if newrelic:  # pragma: no cover
        newrelic.agent.add_custom_parameter('course_id', str(course_key))
        newrelic.agent.add_custom_parameter('org', str(course_key.org))


def set_custom_metrics_for_course_key(course_key):  # pragma: no cover
    """
    Deprecated method to set monitoring custom attributes for course key.
    """
    msg = "Use 'set_custom_attributes_for_course_key' in place of 'set_custom_metrics_for_course_key'."
    warnings.warn(msg, DeprecationWarning)
    set_custom_attribute('deprecated_set_custom_metric_for_course_key', True)
    set_custom_attributes_for_course_key(course_key)


def set_custom_attribute(key, value):
    """
    Set monitoring custom attribute.

    This is not cached, and only support reporting to New Relic Insights.

    """
    if newrelic:  # pragma: no cover
        # note: parameter is new relic's older name for attributes
        newrelic.agent.add_custom_parameter(key, value)


def set_custom_metric(key, value):  # pragma: no cover
    """
    Deprecated method to set monitoring custom attribute.
    """
    msg = "Use 'set_custom_attribute' in place of 'set_custom_metric'."
    warnings.warn(msg, DeprecationWarning)
    set_custom_attribute('deprecated_set_custom_metric', True)
    set_custom_attribute(key, value)
