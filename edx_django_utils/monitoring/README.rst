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
   * - Create a new span (``function_trace``)
     - ✅
     - ❌
     - ✅
   * - Set local root span name (``set_monitoring_transaction_name``)
     - ✅
     - ❌
     - ✅
   * - Manipulate spans (``ignore_transaction``)
     - ✅
     - ❌
     - ❌
   * - Record exceptions (``record_exception``)
     - ✅
     - ✅
     - ✅

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
        'edx_django_utils.monitoring.MonitoringSupportMiddleware',
        'edx_django_utils.monitoring.DeploymentMonitoringMiddleware',
        'edx_django_utils.monitoring.CookieMonitoringMiddleware',
        'edx_django_utils.monitoring.CodeOwnerMonitoringMiddleware',
        'edx_django_utils.monitoring.FrontendMonitoringMiddleware',
        'edx_django_utils.monitoring.MonitoringMemoryMiddleware',
    )

Monitoring Support Middleware and Monitoring Plugins
----------------------------------------------------

The middleware ``MonitoringSupportMiddleware`` provides a number of monitoring capabilities:

* It enables plugging in outside monitoring capabilities, by sending the signals ``monitoring_support_process_request``, ``monitoring_support_process_response``, and ``monitoring_support_process_exception``. These can be useful because this middleware should be available in all Open edX services, and should appear early enough in the list of middleware to monitor most requests, even those that respond early from another middleware.
* It allows certain utility methods, like ``accumulate`` and ``increment``, to work appropriately.
* It adds error span tags to the root span.

In order to use the monitoring signals, import them as follows::

    from edx_django_utils.monitoring.signals import monitoring_support_process_response

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
In addition to adding the FrontendMonitoringMiddleware, you will need to enable a waffle switch ``edx_django_utils.monitoring.enable_frontend_monitoring_middleware`` to enable the frontend monitoring.

Monitoring Memory Usage
-----------------------

In addition to adding the MonitoringMemoryMiddleware, you will need to enable a waffle switch ``edx_django_utils.monitoring.enable_memory_middleware`` to enable the additional monitoring.
