Monitoring Utils
================

This is our primary abstraction from 3rd party monitoring libraries such as newrelic.agent. It includes middleware and utility methods for adding custom attributes and for better monitoring memory consumption.

See ``__init__.py`` for a list of everything included in the public API.

If, for some reason, you need low level access to the newrelic agent, please extend this library to implement the feature that you want. Applications should never include ``import newrelic.agent`` directly.

Choice of monitoring tools
--------------------------

The most complete feature support is for New Relic (the default), but there is also initial support for OpenTelemetry and Datadog.

The Django setting ``OPENEDX_TELEMETRY`` can be set to a list of implementations, e.g. ``['edx_django_utils.monitoring.NewRelicBackend', 'edx_django_utils.monitoring.OpenTelemetryBackend']``. All of the implementations that can be loaded will be used for all applicable telemetry calls.

Feature support matrix for built-in telemetry backends:

.. list-table::
   :header-rows: 1
   :widths: 55, 15, 15, 15

   * -
     - New Relic
     - OpenTelemetry
     - Datadog
   * - Custom span attributes (``set_custom_attribute``, ``accumulate``, ``increment``,  etc.)
     - ✅ (on root span)
     - ✅ (on current span)
     - ✅ (on root span)
   * - Retrieve and manipulate spans (``function_trace``, ``get_current_transaction``, ``ignore_transaction``, ``set_monitoring_transaction_name``)
     - ✅
     - ❌
     - ❌
   * - Record exceptions (``record_exception``)
     - ✅
     - ✅
     - ✅
   * - Instrument non-web tasks (``background_task``)
     - ✅
     - ❌
     - ❌

Additional requirements for using these backends:

- ``edx_django_utils.monitoring.NewRelicBackend``:

  - Install the ``newrelic`` Python package
  - Initialize newrelic, either via the ``newrelic-admin run-program`` wrapper or ``newrelic.agent`` API calls during server startup

- ``edx_django_utils.monitoring.OpenTelemetryBackend``:

  - Install the ``opentelemetry-api`` Python package
  - Initialize opentelemetry, either via the ``opentelemetry-instrument`` wrapper or ``opentelemetry.instrumentation`` API calls during server startup

- ``edx_django_utils.monitoring.DatadogBackend``:

  - Install the ``ddtrace`` Python package
  - Initialize ddtrace, either via the ``ddtrace-run`` wrapper or ``ddtrace.auto`` API calls during server startup

Using Custom Attributes
-----------------------

For help writing and using custom attributes, see docs/how_tos/using_custom_attributes.rst.

Setting up Middleware
---------------------

Here is how you add the middleware:

.. code-block::

    MIDDLEWARE = (
        'edx_django_utils.cache.middleware.RequestCacheMiddleware',

        # Add monitoring middleware immediately after RequestCacheMiddleware
        'edx_django_utils.monitoring.DeploymentMonitoringMiddleware',
        'edx_django_utils.monitoring.CookieMonitoringMiddleware',
        'edx_django_utils.monitoring.CodeOwnerMonitoringMiddleware',
        'edx_django_utils.monitoring.CachedCustomMonitoringMiddleware',
        'edx_django_utils.monitoring.FrontendMonitoringMiddleware',
        'edx_django_utils.monitoring.MonitoringMemoryMiddleware',
    )

Cached Custom Monitoring Middleware
-----------------------------------

The middleware ``CachedCustomMonitoringMiddleware`` is required to allow certain utility methods, like ``accumulate`` and ``increment``, to work appropriately.

Code Owner Custom Attribute
---------------------------

See docstring for ``CodeOwnerMonitoringMiddleware`` for configuring the ``code_owner`` custom attribute for your IDA.

Cookie Monitoring Middleware
----------------------------

See docstring for configuring ``CookieMonitoringMiddleware`` to monitor cookie header size.

Also see ``monitoring/scripts/process_cookie_monitoring_logs.py`` for processing log messages.

Deployment Monitoring Middleware
--------------------------------

Simply add ``DeploymentMonitoringMiddleware`` to monitor the python and django version of each request. See docstring for details.

Frontend Monitoring Middleware
--------------------------------

This middleware ``FrontendMonitoringMiddleware`` inserts frontend monitoring related HTML script tags to the response, see docstring for details.

Monitoring Memory Usage
-----------------------

In addition to adding the MonitoringMemoryMiddleware, you will need to enable a waffle switch ``edx_django_utils.monitoring.enable_memory_middleware`` to enable the additional monitoring.
