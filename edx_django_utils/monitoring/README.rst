Monitoring Utils
================

Includes middleware and utility methods for adding custom metrics and for
better monitoring memory consumption.

Here is how you add the middleware::

.. code-block::

    MIDDLEWARE_CLASSES = (
        'edx_django_utils.cache.middleware.RequestCacheMiddleware',
        ...
        # Monitoring middleware must come after RequestCacheMiddleware
        'edx_django_utils.monitoring.middleware.MonitoringCustomMetricsMiddleware',
        'edx_django_utils.monitoring.middleware.MonitoringMemoryMiddleware',
    )

Monitoring Enhancements and Custom Metrics
__________________________________________

In addition to adding the MonitoringCustomMetricsMiddleware, the public methods
for adding additional enhanced metrics and monitoring are listed in the
``__init__.py`` file.

Monitoring Memory Usage
_______________________

For the MonitoringMemoryMiddleware, you will also need to enable a waffle
switch ``edx_django_utils.monitoring.enable_memory_middleware`` when you
actually wish to enable the additional monitoring.



