Purpose of this Repo
====================

Status
------

Accepted

Context
-------

When creating some caching utilities in Ecommerce, we wanted the ability to share the utilities across IDAs, without the overhead of creating a unique repository for every cross-cutting concern.


Decision
--------

This repository was created as a home for django utilities that might be useful to OpenEdx.

.. note:: Some utilities may warrant their own repository. A judgement call needs to be made as to whether code properly belongs here or not. Please review with the Architecture Team if you have any questions.


Consequences
------------

Certain tools that were created in edx-platform(or other IDAs) will be moved to this shared library.
