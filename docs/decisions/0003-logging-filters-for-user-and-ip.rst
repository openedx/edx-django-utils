Logging filters for user and IP
================================================

Status
------

Proposed

Context
-------

As part of the Security Working Group's work on SEG-34, we decided it would be best to store the logging filters for
LMS users and remote IP addresses in this library, so these filters may be re-used by any edx component. Of particular
use, we can update the logging settings in the IDA cookie-cutter repo to reference these filters in the standard
logging context that is created from the repo for new IDAs.

Decision
--------


Consequences
------------

