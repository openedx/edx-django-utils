Public API and App Organization
===============================

Status
------

Accepted

Context
-------

The original apps in the library (e.g. ``cache`` and ``monitoring``) exposed a public API via ``__init__.py``.

There are several problems with the original organization of the app code:

* It was easy to forget to add new code to the public API, or ignore this requirement. For example, the Middleware didn't follow the same process.
* It was easy for a user of the library to mistakenly use code from a different module in the app, rather than through the public API.

Decision
--------

All implementation code should be moved to an ``internal`` module.

using monitoring as an example, the public API would be exposed as follows in ``edx_django_utils/monitoring/__init__.py``::

    from .internal.somemodule import ...

The benefits of this setup include:

* A clear designation of what is part of the public API.
* The ability to refactor the implementation without changing the API.
* A clear reminder to developers adding new code that it needs to be exposed if it is public.
* A clear reminder to developers using the library not to use code from the internal implementation.

Consequences
------------

Whenever a new class or function is added to the edx_django_utils public API, it should be implemented in the Django app's ``internal`` module and explicitly imported in its ``__init__.py`` module.

Additionally, some existing apps will need to be refactored.
