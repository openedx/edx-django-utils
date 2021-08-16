User and Group Management Commands
==================================

Context
-------

Open edX administrators ocassionally need to grant permissions to staff users for certain django services (e.g. ecommerce, registrar). Right now, this is done manually via django admin of the django service. This method of granting permissions is not endorsed, since it is difficult to review, audit, and track changes to user access over time.

edx-platform, however, defines ``manage_user`` and ``manage_group`` management commands, which allow users to be managed via an external system (such as one, for example, that defines permissions declaratively in version-controlled YAML). These user and group management commands are supposedly generic enough to be used via a common library/app (such as edx-django-utils) so that this users and group management scheme can be brought to other IDAs.

Decision
--------

User and group management commands should be moved to edx-django-utils from edx-platform so that the commands are available to other services.

The original idea for this decision came from an `edx.org private discussion on app permissions`_.

.. _`edx.org private discussion on app permissions`: https://github.com/edx/app-permissions/blob/master/docs/known-issues.md#it-only-works-on-edxapp

