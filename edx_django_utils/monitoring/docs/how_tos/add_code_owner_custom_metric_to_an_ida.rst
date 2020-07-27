Add Code_Owner Custom Metric to an IDA
======================================

.. contents::
   :local:
   :depth: 2

What is the code_owner custom metric?
-------------------------------------

The code_owner custom metric can be used to create custom dashboards and alerts for monitoring the things that you own. It was originally introduced for the LMS, as is described in this `ADR on monitoring by code owner`_.

You can now easily add this same metric to any IDA so that your dashboards and alerts can work across multiple IDAs at once.

If you want to know about custom metrics in general, see: using_custom_metrics.rst.

.. _ADR on monitoring by code owner: https://github.com/edx/edx-platform/blob/master/lms/djangoapps/monitoring/docs/decisions/0001-monitoring-by-code-owner.rst

Setting up the Middleware
-------------------------

You simply need to add ``edx_django_utils.monitoring.code_owner.middleware.CodeOwnerMetricMiddleware`` as described in the README to make this functionality available. Then it is ready to be configured.

Configuring your app settings
-----------------------------

Once the Middleware is made available, simply set the Django Setting ``CODE_OWNER_MAPPINGS`` appropriately.

The following example shows how you can include an optional config for a catch-all using ``'*'``. Although you might expect this example to use Python, it is intentionally illustrated in YAML because the catch-all requires special care in YAML.

::

    # YAML format of example CODE_OWNER_MAPPINGS
    CODE_OWNER_MAPPINGS:
      team-red:
        - xblock_django
        - openedx.core.djangoapps.xblock
      team-blue:
      - '*'  # IMPORTANT: you must surround * with quotes in yml

How to find and fix code_owner mappings
---------------------------------------

If you are missing the `code_owner` custom metric on a particular Transaction or Error, or if `code_owner` is matching the catch-all, but you want to add a more specific mapping, you can use the other `code_owner supporting metrics`_ to determine what the appropriate mappings should be.

.. _code_owner supporting metrics: https://github.com/edx/edx-django-utils/blob/7db8301af21760f8bca188b3c6c95a8ae873baf7/edx_django_utils/monitoring/code_owner/middleware.py#L28-L34
