Enhanced Monitoring and Custom Metrics
======================================

.. contents::
   :local:
   :depth: 2

What is a Custom Metrics?
-------------------------

A custom metric is a name/value pair that you define, which will be associated with a request and available in various places in your monitoring software. For example, in Open edX, there is a ``request_user_id`` made available to all requests using the `RequestMetricsMiddleware`_.

If you are using NewRelic, you can search for PageVeiws, Transactions, TransactionErrors, etc. using NewRelic Insights, either with custom queries using the Data Explorer (searching "Events", not Metrics). They will also appear in other places, like when viewing an error in NewRelic APM.

.. _RequestMetricsMiddleware: https://github.com/edx/edx-drf-extensions/blob/master/edx_rest_framework_extensions/middleware.py#L12-L39

Coding New Custom Metrics
-------------------------

After setting up Middleware as detailed in README.rst, adding a new custom metric is as simple as::

    from openedx.core.djangoapps import monitoring_utils

    monitoring_utils.set_custom_metric(name, value)

* Supported values are strings, bools and numbers.
* Earlier values will be overwritten if the same name is set multiple times during a request.

The following methods only work with number values, and do *not* overwrite earlier values, but instead make use of earlier values within a request::

    monitoring_utils.accumulate(name, value)
    monitoring_utils.increment(name, value)

For a complete list of the public methods available, see the ``__init__.py`` file and the docstrings for details.

If you require functionality from ``newrelic.agent`` that hasn't yet been abstracted, please add any additional functionality to keep it encapsulated.

Tips for Using Custom Metrics
-----------------------------

* A single name with an enum-like string value is often better than a set of related names with boolean values. For example:

  * **DO**:

    * request_auth_type: unauthenticated/jwt-cookie/session

  * **DON'T** do:

    * is_request_unauthenticated: True/False,
    * is_request_auth_jwt_cookie: True/False,
    * is_request_auth_session: True/False.

* When possible, set the custom metric for both the positive and negative case. This helps avoid misinterpreting an incorrect query that doesn't turn up a metric.
* Easily check a custom metric across multiple environments (``appName`` in NewRelic).  For example, for edx.org, this means checking Production and Edge, where Edge might often be forgotten.
* Avoid dynamic metric names. More than 2000 metrics (for NewRelic) may cause issues.

Common Use Cases for Custom Metrics
-----------------------------------

Although logging could also be used, with custom metrics, you don't need to worry about blowing out the logs if it is called many times, and you can query it along with all the pre-existing custom metrics.

Consider using ``temp_`` as a prefix to any metric name you plan to remove soon after it is added.

Deprecating/Removing Code
~~~~~~~~~~~~~~~~~~~~~~~~~

Ever wonder if some code is actually used or not in Production? Add a temporary custom metric and query it in Production.

In addition to `Tips for Using Custom Metrics`_, remember to:

* Check the ``appName`` to see where code might only be used in a Stage environment.
* Check Transaction ``response.status`` to see if code is being used on successful transactions.
* Use ``metric-name is not null`` to find all rows with a value.
* Look at the metric values in addition to getting non-null counts.  A value of 'None' is not null, but would be counted.
* If the metric is added to a library, ensure all applications have the upgraded library before deciding whether or not the code is in use.

Debugging Production Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add a temporary custom metric to gain visibility into code running in Production. If using NewRelic, the custom metric will also be associated with the error in the case of debugging errors.

If you are seeing unexpected failures in Insights, review Transaction ``request.method`` and ``request_user_agent`` to see if bots are making unexpected calls that are failing.

Refactoring Code
~~~~~~~~~~~~~~~~

Want to dark launch some refactored code and ensure it works before switching to it? Add temporary metrics for the old value, new value, and whether they differ. This will provide quick insight into whether or not there is an issue, and if so, potentially why.

Advanced Cases with Caching
~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to track something like an ordered list built up at different points in a request, you could add the list to a RequestCache, and update both the cached version and the metric with every change. This enables you to look-up the old value and append to it as needed.

For example, this could be used to track Authentication classes or Permission classes used.

NewRelic Query Language Examples
--------------------------------

If you are using NewRelic Insights, here are some NewRelic Query Language (NRQL) examples using existing custom metrics.

Simpler NRQL examples
~~~~~~~~~~~~~~~~~~~~~

Successful Transactions in Production::

  SELECT * from Transaction
  WHERE appName LIKE 'prod%' AND response.status LIKE '2%'
  SINCE 1 week ago LIMIT 50

Production error counts by code_owner::

  SELECT count(*) from TransactionError
  WHERE appName LIKE 'prod%' AND code_owner IS NOT NULL
  FACET code_owner, appName
  SINCE 1 week ago LIMIT 50

Advanced NRQL examples
~~~~~~~~~~~~~~~~~~~~~~

Front end load times for the courseware index view rendering, faceted by org::

  SELECT count(*), percentile(duration, 50), percentile(duration, 95), percentile(duration, 99)
  from PageView where appName='prod-edx-edxapp-lms' and name='WebTransaction/Function/courseware.views:index'
  facet org since 1 week ago limit 100

Comparing load times for sequences that have LTI components and those that don't::

  SELECT filter(percentile(duration, 50), where `seq.current.block_counts.lti` is NULL) as 'No LTI',
  filter(percentile(duration, 50), where `seq.current.block_counts.lti` > 0) as LTI
  FROM PageView where appName='prod-edx-edxapp-lms' and name='WebTransaction/Function/courseware.views:index'
  since 1 week ago

For more help, see `NewRelic Resources`_.

NewRelic Resources
------------------

Although the point of these monitoring utilities are to abstract away a given implementation, ultimately, if you are using NewRelic it can be helpful to know how it works.

* `APM Python Agent API`_
* `NewRelic Query Language (NRQL)`_

.. _APM Python Agent API: https://docs.newrelic.com/docs/agents/python-agent/api-guides/guide-using-python-agent-api
.. _NewRelic Query Language (NRQL): https://docs.newrelic.com/docs/query-data/nrql-new-relic-query-language/getting-started/introduction-nrql
