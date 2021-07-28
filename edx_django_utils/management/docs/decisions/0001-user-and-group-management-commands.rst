User and Group Management Commands
===============================

Context
-------

Open edX administrators ocassionally need to grant permissions to users for certain django services (e.g. ecommerce, registrar). Right now, this is done manually via django admin of the django app. This method of granting permissions is not endorsed.

The user and group management commands in edx-platform, are supposedly generic enough to be used via a common library/app so that users and groups can be managed without much (repeated) modificaiton to IDAs.

Decision
--------

User and group management commands should be moved to edx-django-utils (this repository) from edx-platform and edx_django_utils should be added to INSTALLED_APPS section of all django apps so that the user and group management commands are available to the apps.

Kyle's notes can be found `here https://github.com/edx/app-permissions/pull/1454/files#diff-ab850bbacf01a93fe03d0d87d0ed5d2db2f1e1d1d27c7057eb556e63b084c4e7R7-R48`.

Consequences
------------

