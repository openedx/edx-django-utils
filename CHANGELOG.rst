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
----------

[4.4.1] - 2021-12-17
--------------------

Updated
_______

* Replaced usage of 'django.conf.urls.url()' with 'django.urls.re_path()'

[4.4.0] - 2021-09-02
--------------------

Added
_______

* Added ``DeploymentMonitoringMiddleware`` to record ``Python`` and ``Django`` versions in NewRelic with each transaction.

[4.3.0] - 2021-07-20
--------------------

Added
_______

* Added user and group management utilities.

[4.2.0] - 2021-07-14
--------------------

Added
_______

* Added support for Django 3.1 and 3.2

[4.1.0] - 2021-06-01
--------------------

Added
_______

* Added mixin for a custom Django admin class which disables CRUD operation on the admin's model.

Added
_______

* Script new_relic_nrql_search.py to search the NRQL in New Relic alert policies and dashboards using a supplied regex.

[4.0.0] - 2021-05-03
--------------------

Removed
_______

* Removed the old location of ``CodeOwnerMonitoringMiddleware``. It had moved in a past commit. Although technically a breaking change, all references in the Open edX platform have already been updated to point to the new location.

Added
_____

* Added new ``code_owner_theme`` and ``code_owner_squad`` custom attributes. This is useful in cases where the ``code_owner`` combines a theme and squad name, because monitoring can instead reference ``code_owner_squad`` to be resilient to theme name updates. For the decision doc, see edx_django_utils/monitoring/docs/decisions/0004-code-owner-theme-and-squad.rst.

Updated
_______

* Misconfigurations of CODE_OWNER_MAPPINGS will now fail fast, rather than just logging. Although technically a breaking change, if CODE_OWNER_MAPPINGS is in use, it is probably correctly configured and this change should be a no-op.

[3.16.0] - 2021-03-24
---------------------

Added
_____

* Added ``pluggable_override`` decorator.


[3.15.0] - 2021-03-02
---------------------

* Added chunked_queryset utility.

[3.14.0] - 2020-12-15
---------------------

Removed
_______

* Dropped support for Python 3.5.


[3.13.0] - 2020-11-18
---------------------

Added
_____

* Added record_exception to monitor caught exceptions.

Updated
_______

* Added additional details to the `deprecated_monitoring_utils` custom attribute values to make it simpler to track down usage.

[3.12.0] - 2020-11-17
---------------------

Added
_____

* Added set_code_owner_attribute decorator for use with celery tasks.
* Added set_code_owner_attribute_from_module as an alternative to the decorator.

Updated
_______

* Cleaned up some of the code owner middleware code. In doing so, renamed custom attribute code_owner_path_module to code_owner_module. This may affect monitoring dashboards. Also slightly changed when error custom attributes are set.

[3.11.0] - 2020-10-31
---------------------

Added
_____

* Added ADR 0004-public-api-and-app-organization.rst to explain a new app organization, which makes use of the public API more consistent.

Updated
_______

* Applied the new app organization described in th ADR to the monitoring Django app.
* Moved CachedCustomMonitoringMiddleware, CodeOwnerMonitoringMiddleware, and MonitoringMemoryMiddleware to the public API.

Deprecated
__________

* Deprecated the old locations of CachedCustomMonitoringMiddleware, CodeOwnerMonitoringMiddleware, and MonitoringMemoryMiddleware.
* Deprecated various methods from modules that were always meant to be used from the public API.

  * accumulate
  * increment
  * set_custom_attribute
  * set_custom_attributes_for_course_key

* Added additional custom attributes for deprecated classes and methods to make them safer to retire.

.. note::

  Some method implementations that were available in the public API were moved without adding a deprecated equivalent. These were not found when searching, so hopefully they are only used via the public API, which did not change. This includes functions in ``transactions.py`` and ``code_owner/utils.py``.

Removed
_______

* Removed the middleware ordering checks. This is not a typical Django feature and it is painful when refactoring.

[3.10.0] - 2020-10-28
---------------------

Added
_______

* Added logging filter classes for users and remote IP addresses to be used by all IDAs. These were moved here from edx-platform.

[3.9.0] - 2020-10-21
--------------------

Updated
_______

* Exposed existing get_code_owner_from_module via the public api.
* Fixed get_code_owner_from_module to not require a call to is_code_owner_mappings_configured beforehand.
* Set the existing code_owner_path_module custom attribute, even for cases where the transaction name was used, rather than the view module.
* Refactor code owner setting processing.

[3.8.0] - 2020-08-31
--------------------

Updated
_______

* Renamed "custom metric" to "custom attribute" throughout the monitoring library. This decision can be read about in the ADR 0002-custom-monitoring-language.rst.  The following have been deprecated:

  * set_custom_metric (use set_custom_attribute)
  * set_custom_metrics_for_course_key (use set_custom_attributes_for_course_key)
  * MonitoringCustomMetricsMiddleware (use CachedCustomMonitoringMiddleware)
  * CachedCustomMonitoringMiddleware.accumulate_metric (use CachedCustomMonitoringMiddleware.accumulate_attribute)

    * This wasn't meant to be used publicly, but was deprecated just in case.

  * CodeOwnerMetricMiddleware (use CodeOwnerMonitoringMiddleware)

[3.7.4] - 2020-08-29
--------------------

* Fix to custom monitoring accumulate to actually accumulate rather than overwrite.

[3.7.3] - 2020-08-12
--------------------

Updated
_______

* Upgrade psutil to latest version

[3.7.2] - 2020-08-10
--------------------

Updated
_______

* Added missing classes to plugins public api. See ``plugins.__init__.py`` for latest api.
* Updated plugin method names to be more descriptive. See ``plugins.__init__.py`` for latest.

.. note:: Although these changes are backwards incompatible, they are being added as a bug fix because plugins code release (3.7.0) is not yet in use.

[3.7.1] - 2020-08-10
--------------------

Updated
_______

* Exposing all public functions in edx_django_utils/plugins directory in its __init__.py file.
    * this was done to keep inline with standard/pattern used in other packages in edx_django_utils

[3.7.0] - 2020-08-10
--------------------

Added
_____

* Adding Plugin infrastructure
    * Allows IDAs to use plugins

[3.6.0] - 2020-08-04
--------------------

Added
_____

* Improved documentation for CodeOwnerMetricMiddleware, including a how_tos/add_code_owner_custom_metric_to_an_ida.rst for adding it to a new IDA.
* Added ignore_transaction monitoring utility to ignore transactions we don't want tracked.

Updated
_______

* Moved transaction-related monitoring code into it's own file. Still exposed through `__init__.py` so it's a non-breaking change.

[3.5.0] - 2020-07-22
--------------------

Updated
_______

* Added a catch-all capability to CodeOwnerMetricMiddleware when CODE_OWNER_MAPPINGS includes a '*' as a team's module. The catch-all is used only if there is no other match.

[3.4.0] - 2020-07-20
--------------------

Added
_____

* Added get_current_transaction for monitoring that returns a transaction object with a name property.

Updated
_______

* Updated CodeOwnerMetricMiddleware to use NewRelic's current transaction for cases where resolve() doesn't work to determine the code_owner, like for Middleware.

[3.3.0] - 2020-07-16
--------------------

Added
_____

* CodeOwnerMetricMiddleware was moved here (from edx-platform) in order to be able to take advantage of the ``code_owner`` metric in other IDAs. For details on this decision, see the `ADR for monitoring code owner`_. See the docstring for more details on usage.

.. _ADR for monitoring code owner: https://github.com/edx/edx-django-utils/blob/master/edx_django_utils/monitoring/docs/decisions/0001-monitoring-by-code-owner.rst

[3.2.3] - 2020-05-30
------------------------------------------------
* Removed ceninusepy3 usage.

[3.2.2] - 2020-05-04
------------------------------------------------
* Added support for python 3.8 and dropped support for Django versions older than 2.2

[3.2.1] - 2020-04-17
------------------------------------------------

Changed
_______

* imported get_cache_key in cache/__init__.py.

[3.2.0] - 2020-04-09
------------------------------------------------

Added
_______

* Added get_cache_key utility.

[2.0.1] - 2019-10-09
------------------------------------------------

Changed
_______

* Fixed: Updated function tracing to accomodate changes in New Relic's 5.x Agent.

[2.0.0] - 2019-07-07
------------------------------------------------

Changed
_______

* Converted Middleware (from old style MIDDLEWARE_CLASSES to MIDDLEWARE).
* Removed support for Django versions < 1.11

[1.0.1] - 2018-09-07
------------------------------------------------

Changed
_______

* Fixed: RequestCache now properly uses thread.local.
* Fixed: CachedResponse.__repr__ now handles unicode.

[1.0.0] - 2018-08-28
------------------------------------------------

Added
_______

* Add ``data`` dict property to better match legacy RequestCache interface.

Changed
_______

* Change is_hit/is_miss to is_found.

[0.5.1] - 2018-08-17
------------------------------------------------

Changed
_______

* Fixed bug in TieredCacheMiddleware dependency declaration.

[0.5.0] - 2018-08-16
------------------------------------------------

Changed
_______

* Restored Python 3 support.
* Refactor/clean-up, including Middleware dependency checking.
* Docs updates and other cookiecutter updates.

[0.4.1] - 2018-08-10
------------------------------------------------

Changed
_______

* Split out TieredCacheMiddleware from RequestCacheMiddleware.

[0.4.0] - 2018-08-10
------------------------------------------------

Changed
_______

* Rename CacheUtilsMiddleware to RequestCacheMiddleware.

[0.3.0] - 2018-08-02
------------------------------------------------

Removed
_______

* Temporarily dropped Python 3 support to land this.

[0.2.0] - 2018-08-01
------------------------------------------------

Added
_____

* Added cache and monitoring utilities.


[0.1.0] - 2018-07-23
------------------------------------------------

Added
_____

* First release on PyPI.
