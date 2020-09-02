Custom Monitoring Language
==========================

Status
------

Accepted

Context
-------

Although the monitoring library is meant to encapsulate monitoring functionality, our primary implementation works with New Relic. New Relic has the concept of "events" (with "attributes") and "metrics". However, this library was original written using the term "metric" when referring to New Relic "attributes", and not for New Relic "metrics".

Decision
--------

When referring to New Relic event attributes, we will use the term "attribute", and not the word "metric". We will continue to use the term "custom" for attributes that we define, rather than those that come standard from New Relic.  Note: New Relic uses the terms "attribute" and "parameter" interchangeably, but the term "attribute" is more popular in the UI.

Additionally, we will use the term "custom monitoring" as a more general term for any of our custom additions for monitoring purposes, whether this refers to "custom events", "custom attributes", or "custom metrics".

Consequences
------------

* Switching from "metric" to "attribute" enables us to save the term "metric" for when and if we encapsulate methods that actually write New Relic metrics.
* Because many methods will need to be renamed, we will deprecate the older methods and classes to maintain backward-compatibility until we retire all uses of the old names.

Resources
---------

* `New Relic custom events`_

  * `New Relic custom attributes`_

* `New Relic custom metrics`_

.. _New Relic custom events: https://docs.newrelic.com/docs/insights/event-data-sources/custom-events
.. _New Relic custom attributes: https://docs.newrelic.com/docs/insights/event-data-sources/custom-events/new-relic-apm-report-custom-attributes
.. _New Relic custom metrics: https://docs.newrelic.com/docs/agents/manage-apm-agents/agent-data/collect-custom-metrics
