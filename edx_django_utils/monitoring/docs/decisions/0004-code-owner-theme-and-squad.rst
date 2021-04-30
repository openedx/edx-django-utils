Code Owner Theme and Squad
==========================

Status
------

Accepted

Context
-------

As detailed in the `Monitoring by Code Owner ADR`_, we added a ``code_owner`` custom attribute for monitoring by code owner. The value for this attribute had the format 'theme-squad'.

The problems with this configuration is that for theme name changes, or when squads transfer themes, any monitoring referencing the full name would also need to be updated.

.. _Monitoring by Code Owner ADR: https://github.com/edx/edx-platform/blob/master/lms/djangoapps/monitoring/docs/decisions/0001-monitoring-by-code-owner.rst

Decision
--------

We will add a ``code_owner_squad`` custom attribute. Monitoring will now be able to refer to ``code_owner_squad`` with a value of 'squad', and will be unaffected by theme name changes.

Additionally, we are adding ``code_owner_theme`` for similar convenience if there is a need for theme-based monitoring.

We will leave the original ``code_owner`` custom attribute for backward compatability, and for cases where theme and squad are not used.

Consequences
------------

* Theme name changes may now result in a one time fix for those that were relying on ``code_owner``. Monitoring can switch from ``code_owner`` to ``code_owner_squad``, rather than a change for every theme update in the future.
