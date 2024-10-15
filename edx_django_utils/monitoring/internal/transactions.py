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
