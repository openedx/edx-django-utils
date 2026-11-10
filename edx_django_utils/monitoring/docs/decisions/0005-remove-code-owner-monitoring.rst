Remove Code Owner Monitoring
============================

Status
------

Accepted

Date
----

2026-08-11

Context
-------

Code-owner monitoring functionality in this package was originally introduced for
specific operational needs and later adopted in Open edX services. The maintainers
have since migrated away from this approach and no longer need these package-level
helpers.

The deprecated code-owner components also add ongoing maintenance overhead:

* public API exports for code-owner middleware and helper methods
* celery decorator-based instrumentation guidance
* dedicated scripts and tests tied to New Relic and code-owner mappings
* historical ADRs that no longer describe the active architecture

Decision
--------

We will remove code-owner monitoring implementation and related integration
artifacts from this package.

We will retain historical ADRs and mark them obsolete instead of deleting them:

* ``0001-monitoring-by-code-owner.rst``
* ``0003-code-owner-for-celery-tasks.rst``
* ``0004-code-owner-theme-and-squad.rst``

Consequences
------------

* The following functionality is no longer provided by this package:

  * ``CodeOwnerMonitoringMiddleware``
  * ``set_code_owner_attribute``
  * ``set_code_owner_attribute_from_module``
  * ``get_code_owner_from_module``

* Code-owner-specific scripts, tests, and how-to docs are removed.
* Existing consumers must use their own instrumentation approach where needed.
* Historical decision records remain available and clearly marked obsolete.
