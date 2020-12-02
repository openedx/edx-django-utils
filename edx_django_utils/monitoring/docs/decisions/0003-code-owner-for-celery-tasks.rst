Code Owner for Celery Tasks
===========================

Status
------

Accepted

Context
-------

As detailed in the `Monitoring by Code Owner ADR`_, we were able to add a ``code_owner`` custom attribute to web transactions using a special middleware. Since middleware is not run for celery tasks (non-web transactions), this solution cannot be used.

.. _Monitoring by Code Owner ADR: https://github.com/edx/edx-platform/blob/master/lms/djangoapps/monitoring/docs/decisions/0001-monitoring-by-code-owner.rst

Decision
--------

We implemented a ``@set_code_owner_attribute`` decorator that would add the ``code_owner`` custom attribute for a celery task, and added the decorator to all the celery tasks.  See the `celery section of the code_owner how-to`_ for usage details.

.. _celery section of the code_owner how-to: https://github.com/edx/edx-django-utils/blob/6ed6de25d487314faa01ed72afd190db95afd1e8/edx_django_utils/monitoring/docs/how_tos/add_code_owner_custom_attribute_to_an_ida.rst#handling-celery-tasks

Consequences
------------

* We added the new decorator as needed for all existing tasks.
* New celery tasks will need to add the same decorator. See "Rejected Alternatives" for a potential alternative.

(Rejected) Alternatives
-----------------------

An untested potential alternative to the ``@set_code_owner_attribute`` decorator is to try celery's `task_prerun signal`_ in an IDA, which would also ensure all future celery tasks are automatically handled. Although this is a potentially superior solution, it was missed at the time of implementation. We will not be switching to this solution at this time given we have a working solution and other priorities, but it is a potentially viable solution if the need arises.

Additionally, if this alternative solution were implemented, it would be best to not add celery as a dependency to this library, and to document a new edx-platform implementation. It is unlikely that the solution will be needed outside of edx-platform.

.. _task_prerun signal: https://docs.celeryproject.org/en/stable/userguide/signals.html#task-prerun
