==========
Change Log
==========

..
   All enhancements and patches to edx_django_utils will be documented
   in this file.  It adheres to the structure of http://keepachangelog.com/ ,
   but in reStructuredText instead of Markdown (for ease of incorporation into
   Sphinx documentation and the PyPI description).

   This project adheres to Semantic Versioning (http://semver.org/).

.. There should always be an "Unreleased" section for changes pending release.

Unreleased
~~~~~~~~~~


[3.7.0] - 2020-08-10
~~~~~~~~~~~~~~~~~~~~
* Adding Plugin infrastructure
    - Allows IDAs to use plugins

[3.6.0] - 2020-08-04
~~~~~~~~~~~~~~~~~~~~

Added
_____

* Improved documentation for CodeOwnerMetricMiddleware, including a how_tos/add_code_owner_custom_metric_to_an_ida.rst for adding it to a new IDA.
* Added ignore_transaction monitoring utility to ignore transactions we don't want tracked.

Updated
_______

* Moved transaction-related monitoring code into it's own file. Still exposed through `__init__.py` so it's a non-breaking change.

[3.5.0] - 2020-07-22
~~~~~~~~~~~~~~~~~~~~

Updated
_______

* Added a catch-all capability to CodeOwnerMetricMiddleware when CODE_OWNER_MAPPINGS includes a '*' as a team's module. The catch-all is used only if there is no other match.

[3.4.0] - 2020-07-20
~~~~~~~~~~~~~~~~~~~~

Added
_____

* Added get_current_transaction for monitoring that returns a transaction object with a name property.

Updated
_______

* Updated CodeOwnerMetricMiddleware to use NewRelic's current transaction for cases where resolve() doesn't work to determine the code_owner, like for Middleware.

[3.3.0] - 2020-07-16
~~~~~~~~~~~~~~~~~~~~

Added
_____

* CodeOwnerMetricMiddleware was moved here (from edx-platform) in order to be able to take advantage of the ``code_owner`` metric in other IDAs. For details on this decision, see the `ADR for monitoring code owner`_. See the docstring for more details on usage.

.. _ADR for monitoring code owner: https://github.com/edx/edx-django-utils/blob/master/edx_django_utils/monitoring/docs/decisions/0001-monitoring-by-code-owner.rst

[3.2.3] - 2020-05-30
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Removed ceninusepy3 usage.

[3.2.2] - 2020-05-04
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Added support for python 3.8 and dropped support for Django versions older than 2.2

[3.2.1] - 2020-04-17
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Changed
_______

* imported get_cache_key in cache/__init__.py.

[3.2.0] - 2020-04-09
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Added
_______

* Added get_cache_key utility.

[2.0.1] - 2019-10-09
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Changed
_______

* Fixed: Updated function tracing to accomodate changes in New Relic's 5.x Agent.

[2.0.0] - 2019-07-07
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Changed
_______

* Converted Middleware (from old style MIDDLEWARE_CLASSES to MIDDLEWARE).
* Removed support for Django versions < 1.11

[1.0.1] - 2018-09-07
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Changed
_______

* Fixed: RequestCache now properly uses thread.local.
* Fixed: CachedResponse.__repr__ now handles unicode.

[1.0.0] - 2018-08-28
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Added
_______

* Add ``data`` dict property to better match legacy RequestCache interface.

Changed
_______

* Change is_hit/is_miss to is_found.

[0.5.1] - 2018-08-17
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Changed
_______

* Fixed bug in TieredCacheMiddleware dependency declaration.

[0.5.0] - 2018-08-16
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Changed
_______

* Restored Python 3 support.
* Refactor/clean-up, including Middleware dependency checking.
* Docs updates and other cookiecutter updates.

[0.4.1] - 2018-08-10
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Changed
_______

* Split out TieredCacheMiddleware from RequestCacheMiddleware.

[0.4.0] - 2018-08-10
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Changed
_______

* Rename CacheUtilsMiddleware to RequestCacheMiddleware.

[0.3.0] - 2018-08-02
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Removed
_______

* Temporarily dropped Python 3 support to land this.

[0.2.0] - 2018-08-01
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Added
_____

* Added cache and monitoring utilities.


[0.1.0] - 2018-07-23
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Added
_____

* First release on PyPI.
