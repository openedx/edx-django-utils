Change Log
----------

..
   All enhancements and patches to edx_django_utils will be documented
   in this file.  It adheres to the structure of http://keepachangelog.com/ ,
   but in reStructuredText instead of Markdown (for ease of incorporation into
   Sphinx documentation and the PyPI description).
   
   This project adheres to Semantic Versioning (http://semver.org/).

.. There should always be an "Unreleased" section for changes pending release.

Unreleased
~~~~~~~~~~
*

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
