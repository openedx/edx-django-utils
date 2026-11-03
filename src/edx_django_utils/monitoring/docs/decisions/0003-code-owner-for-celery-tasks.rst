Code Owner for Celery Tasks
===========================

Status
------

Accepted

Context
-------

As detailed in the `Monitoring by Code Owner ADR`_, we were able to add a ``code_owner`` custom attribute to web transactions using a special middleware. Since middleware is not run for celery tasks (non-web transactions), this solution cannot be used.

.. _Monitoring by Code Owner ADR: https://github.com/openedx/edx-platform/blob/master/lms/djangoapps/monitoring/docs/decisions/0001-monitoring-by-code-owner.rst

Decision
--------

We implemented a ``@set_code_owner_attribute`` decorator that would add the ``code_owner`` custom attribute for a celery task, and added the decorator to all the celery tasks.  See the `celery section of the code_owner how-to`_ for usage details.

.. _celery section of the code_owner how-to: https://github.com/openedx/edx-django-utils/blob/6ed6de25d487314faa01ed72afd190db95afd1e8/edx_django_utils/monitoring/docs/how_tos/add_code_owner_custom_attribute_to_an_ida.rst#handling-celery-tasks

Consequences
------------

* We added the new decorator as needed for all existing tasks.
* New celery tasks will need to add the same decorator.

(Rejected) Alternatives
-----------------------

Celery has a `task_prerun signal`_ that would allow us to execute code every time a task is about to start.

This possibility was discovered after we had already annotated tasks. We hoped this would ensure all celery tasks were automatically handled rather than requiring explicit decorators. However, when we `trialed the task_prerun approach <https://github.com/openedx/edx-platform/pull/33180>`_ we discovered that no attribute was set on the Celery tasks. This seems to be because New Relic instruments the task function itself with transaction-start and transaction-end calls, so any signals that are run before or after the task execution occur outside the scope of the transaction.

Theoretically, we could do something similar to New Relic's monkeypatching in order to inject a code owner attribute call, but this would be fragile and could lead to disruptive failures.

.. _task_prerun signal: https://docs.celeryproject.org/en/stable/userguide/signals.html#task-prerun

Changelog
---------

* 2023-09-19: Updated ``task_prerun`` alternative with results of a failed attempt at using it.
