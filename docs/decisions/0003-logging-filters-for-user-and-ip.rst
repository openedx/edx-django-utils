Logging filters for user and IP
================================================

Status
------

Proposed

Context
-------

As part of the Security Working Group's work on SEG-34, we recognized that the `logging filters`_ for
LMS users and remote IP addresses were not reusable by other IDAs from inside LMS.

.. _logging filters: https://github.com/edx/edx-platform/blob/11e4cab6220c8c503787142f48a352410191de0a/openedx/core/djangoapps/util/log_utils.py#L16

Decision
--------

We decided to move the LMS users and remote IP addresses to this library, so these filters may be re-used by any edx component. Of particular use, we can update the logging settings in the IDA cookie-cutter repo to reference these filters in the standard logging context that is created from the repo for new IDAs.

Consequences
------------

We will need to:
* Update the IDA cookie-cutter once these are available.
* Remove these classes from edx-platform.
