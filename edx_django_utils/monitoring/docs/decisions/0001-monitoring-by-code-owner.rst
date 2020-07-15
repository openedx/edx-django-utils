Monitoring by Code Owner
************************

Status
======

Accepted

Context
=======

We originally implemented the "code_owner" custom metric in edx-platform for split-ownership of the LMS.  See the original `ADR in edx-platform for monitoring by code owner`_.

Owners wanted to be able to see transactions that they owned, in any IDA.

.. _ADR in edx-platform for monitoring by code owner: https://github.com/edx/edx-platform/blob/59e0f6efcf2a297806918f8e0020255c1f59ea5f/lms/djangoapps/monitoring/docs/decisions/0001-monitoring-by-code-owner.rst

Decision
========

We will move the "code_owner" custom metric code to these shared monitoring utilities so it is available for all IDAs.

The ability to add a catch-all configuration if there are no other matches will also be added in follow-up work.

Consequences
============

IDA owners will be able to add middleware and a Django Setting to have the same "code_owner" metric available across all IDAs that are owned.

At this time, in the case of an IDA with split-ownership, maintenance of the Django Setting is still manual. In other words, new paths with new owners will needed to be added to the setting.  Otherwise, the catch-all (if configured) will be marked as the code owner.
