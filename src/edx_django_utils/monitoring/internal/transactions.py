"""
This is a collection of transaction-related monitoring utilities.

Usage:

    from edx_django_utils.monitoring import ignore_transaction
    ...
    # called from inside a view you want ignored
    ignore_transaction()

Please remember to expose any new methods in the `__init__.py` file.
"""
try:
    import newrelic.agent
except ImportError:
    newrelic = None  # pylint: disable=invalid-name


def ignore_transaction():
    """
    Ignore the transaction in monitoring. Only works for NewRelic.

    This allows us to ignore code paths that are unhelpful to include, such as
    `/health/` checks.

    """
    # Note: This is not being ported over to backends, because we don't have
    # an equivalent for Datadog. For Datadog, use filter/ignore rules.
    if newrelic:  # pragma: no cover
        newrelic.agent.ignore_transaction()
