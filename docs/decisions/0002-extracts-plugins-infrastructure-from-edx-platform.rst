1. Extract plugins Infrastructure from edx-platform
===================================================

Status
------

Draft

Context
-------

We have experimented with adding plugins to edx-platform and are now ready to move this functionality to other IDAs. However, since the plugins infrastructure is currently located in edx-platform and thus not easily usable by IDAs.



Decision
--------

Move plugin infrastructure to edx-django-utils.

Consequences
------------

Fix all links to this code in edx-platform.