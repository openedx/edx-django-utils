1. Extract plugins Infrastructure from edx-platform
===================================================

Status
------

Accepted

Context
-------

We have experimented with adding plugins to edx-platform and are now ready to move this functionality to other IDAs. However, the django app plugins infrastructure is currently located in edx-platform and thus not easily usable by IDAs.

This Django App Plugin functionality allows for Django-framework code to be
encapsulated within each Django app, rather than having a monolith Project that
is aware of the details of its Django apps.


Decision
--------

Move plugin infrastructure to edx-django-utils.

.. note:: currently, it made sense to add plugins to this repository, but if its usage becomes more widespread and it becomes more critical, it might make sense to remove this into its own repository.

.. note:: For now, this code is still very specific to edx-platform. The necessary work to make it more general was not done with this move. The intention was to first get it moved and come back later to make it more general

Consequences
------------

Fix all links to this code in edx-platform.
