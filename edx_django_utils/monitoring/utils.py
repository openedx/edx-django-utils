"""
This is an interface to the monitoring_utils middleware.  Functions
defined in this module can be used to report monitoring custom metrics.

Usage:

    from edx_django_utils import monitoring as monitoring_utils
    ...
    monitoring_utils.accumulate('xb_user_state.get_many.num_items', 4)

There is no need to do anything else.  The metrics are automatically cleared
before the next request.

We try to keep track of our custom metrics at:

https://openedx.atlassian.net/wiki/display/PERF/Custom+Metrics+in+New+Relic

At this time, these custom metrics will only be reported to New Relic.

"""
from contextlib import contextmanager

from . import middleware

try:
    import newrelic.agent
except ImportError:
    newrelic = None  # pylint: disable=invalid-name


def accumulate(name, value):
    """
    Accumulate monitoring custom metric for the current request.

    The named metric is accumulated by a numerical amount using the sum.  All
    metrics are queued up in the request_cache for this request.  At the end of
    the request, the monitoring_utils middleware will batch report all
    queued accumulated metrics to the monitoring tool (e.g. New Relic).

    Arguments:
        name (str): The metric name.  It should be period-delimited, and
            increase in specificity from left to right.  For example:
            'xb_user_state.get_many.num_items'.
        value (number):  The amount to accumulate into the named metric.  When
            accumulate() is called multiple times for a given metric name
            during a request, the sum of the values for each call is reported
            for that metric.  For metrics which don't make sense to accumulate,
            make sure to only call this function once during a request.
    """
    middleware.MonitoringCustomMetricsMiddleware.accumulate_metric(name, value)


def increment(name):
    """
    Increment a monitoring custom metric representing a counter.

    Here we simply accumulate a new custom metric with a value of 1, and the
    middleware should automatically aggregate this metric.
    """
    accumulate(name, 1)


def set_custom_metrics_for_course_key(course_key):
    """
    Set monitoring custom metrics related to a course key.

    This is not cached, and only support reporting to New Relic Insights.

    """
    if newrelic:  # pragma: no cover
        newrelic.agent.add_custom_parameter('course_id', str(course_key))
        newrelic.agent.add_custom_parameter('org', str(course_key.org))


def set_custom_metric(key, value):
    """
    Set monitoring custom metric.

    This is not cached, and only support reporting to New Relic Insights.

    """
    if newrelic:  # pragma: no cover
        newrelic.agent.add_custom_parameter(key, value)


def set_monitoring_transaction_name(name, group=None, priority=None):
    """
    Sets the transaction name for monitoring.

    This is not cached, and only support reporting to New Relic.

    """
    if newrelic:  # pragma: no cover
        newrelic.agent.set_transaction_name(name, group, priority)


@contextmanager
def function_trace(function_name):
    """
    Wraps a chunk of code that we want to appear as a separate, explicit,
    segment in our monitoring tools.
    """
    # Not covering this because if we mock it, we're not really testing anything
    # anyway. If something did break, it should show up in tests for apps that
    # use this code with newrelic enabled, on whatever version of newrelic they
    # run.
    if newrelic:  # pragma: no cover
        if newrelic.version_info[0] >= 5:
            with newrelic.agent.FunctionTrace(function_name):
                yield
        else:
            nr_transaction = newrelic.agent.current_transaction()
            with newrelic.agent.FunctionTrace(nr_transaction, function_name):
                yield
    else:
        yield


class MonitoringTransaction():
    """
    Represents a monitoring transaction (likely the current transaction).
    """
    def __init__(self, transaction):
        self.transaction = transaction

    @property
    def name(self):
        """
        The name of the transaction.

        For NewRelic, the name may look like:
            openedx.core.djangoapps.contentserver.middleware:StaticContentServer

        """
        if self.transaction and hasattr(self.transaction, 'name'):
            return self.transaction.name
        return None


def get_current_transaction():
    """
    Returns the current transaction.
    """
    current_transaction = None
    if newrelic:
        current_transaction = newrelic.agent.current_transaction()

    return MonitoringTransaction(current_transaction)
