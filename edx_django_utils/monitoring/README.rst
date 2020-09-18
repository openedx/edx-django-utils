Monitoring Utils
================

This is our primary abstraction from 3rd party monitoring libraries such as newrelic.agent. It includes middleware and utility methods for adding custom metrics and for better monitoring memory consumption.

If, for some reason, you need low level access to the newrelic agent, please extend this library to implement the feature that you want. Applications should never include ``import newrelic.agent`` directly.

Using Custom Metrics
--------------------

For help writing and using custom metrics, see docs/how_tos/using_custom_metrics.rst.

Setting up Middleware
---------------------

Here is how you add the middleware:

.. code-block::

    MIDDLEWARE = (
        'edx_django_utils.cache.middleware.RequestCacheMiddleware',
        # Generate code ownership metrics. Keep this immediately after RequestCacheMiddleware.
        ...
        # Monitoring middleware must come after RequestCacheMiddleware
        'edx_django_utils.monitoring.code_owner.middleware.CodeOwnerMetricMiddleware',
        'edx_django_utils.monitoring.middleware.MonitoringCustomMetricsMiddleware',
        'edx_django_utils.monitoring.middleware.MonitoringMemoryMiddleware',
    )

Monitoring Memory Usage
-----------------------

In addition to adding the MonitoringMemoryMiddleware, you will need to enable a waffle switch ``edx_django_utils.monitoring.enable_memory_middleware`` to enable the additional monitoring.

Code Owner Custom Metric
------------------------

See docstrings for ``CodeOwnerMetricMiddleware`` for configuring the ``code_owner`` custom metric for your IDA.
