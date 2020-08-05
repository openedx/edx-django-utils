1. Extract plugins Infrastructure from edx-platform
===================================================

Status
------

Accepted

Context
-------

We have experimented with adding plugins to edx-platform and are now ready to move this functionality to other IDAs. However, the django app plugins infrastructure is currently located in edx-platform and thus not easily usable by IDAs.

TODO(jinder): find description of Django plugins and add it here


Decision
--------

Move plugin infrastructure to edx-django-utils.

Note, currently, it made sense to add plugins to this repository, but if its usage becomes more widespread and it becomes more critical, it might make sense to remove this into its own repository.

Consequences
------------

Fix all links to this code in edx-platform.
