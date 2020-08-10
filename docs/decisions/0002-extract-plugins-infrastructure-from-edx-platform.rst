Extract plugins Infrastructure from edx-platform
================================================

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

.. note:: Currently, we've decided this plugin enablement code doesn't warrant its own repository.

Consequences
------------

Fix all links to this code in edx-platform.
