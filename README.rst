edx-django-utils
================

|pypi-badge| |travis-badge| |codecov-badge| |doc-badge| |pyversions-badge|
|license-badge|

EdX utilities for Django Application development.

Note that some utilities may warrant their own repository. A judgement call
needs to be made as to whether code properly belongs here or not. Please
review with the Architecture Team if you have any questions.

Overview
--------

This repository includes shared utilities for:

* `Cache Utilities`_: Includes a RequestCache and a TieredCache.

* `Monitoring Utilities`_: Includes Middleware and utilities for enhanced monitoring.
  At this time, supports NewRelic monitoring.

* `Plugin Infrastructure`_: Enables enhanced Django Plugin capabilities.

.. _Cache Utilities: edx_django_utils/cache/README.rst

.. _Monitoring Utilities: edx_django_utils/monitoring/README.rst

.. _Plugin Infrastructure: edx_django_utils/plugins/README.rst

Documentation
-------------

The full documentation is in the docs directory.

TODO: Publish to https://edx-django-utils.readthedocs.org.

Design Pattern followed by packages
-----------------------------------

All tools in edx_django_utils should expose their public api in their __init__.py files. This entails adding to __init__.py all functions/classes/constants/objects that are intended to be used by users of library.

License
-------

The code in this repository is licensed under the AGPL 3.0 unless
otherwise noted.

Please see ``LICENSE.txt`` for details.

How To Contribute
-----------------

Contributions are very welcome.

Please read `How To Contribute <https://github.com/edx/edx-platform/blob/master/CONTRIBUTING.rst>`_ for details.

Even though they were written with ``edx-platform`` in mind, the guidelines
should be followed for Open edX code in general.

PR description template should be automatically applied if you are sending PR from github interface; otherwise you
can find it it at `PULL_REQUEST_TEMPLATE.md <https://github.com/edx/edx-django-utils/blob/master/.github/PULL_REQUEST_TEMPLATE.md>`_

Issue report template should be automatically applied if you are sending it from github UI as well; otherwise you
can find it at `ISSUE_TEMPLATE.md <https://github.com/edx/edx-django-utils/blob/master/.github/ISSUE_TEMPLATE.md>`_

Reporting Security Issues
-------------------------

Please do not report security issues in public. Please email security@edx.org.

Getting Help
------------

Have a question about this repository, or about Open edX in general?  Please
refer to this `list of resources`_ if you need any assistance.

.. _list of resources: https://open.edx.org/getting-help


.. |pypi-badge| image:: https://img.shields.io/pypi/v/edx-django-utils.svg
    :target: https://pypi.python.org/pypi/edx-django-utils/
    :alt: PyPI

.. |travis-badge| image:: https://travis-ci.org/edx/edx-django-utils.svg?branch=master
    :target: https://travis-ci.org/edx/edx-django-utils
    :alt: Travis

.. |codecov-badge| image:: http://codecov.io/github/edx/edx-django-utils/coverage.svg?branch=master
    :target: http://codecov.io/github/edx/edx-django-utils?branch=master
    :alt: Codecov

.. |doc-badge| image:: https://readthedocs.org/projects/edx-django-utils/badge/?version=latest
    :target: http://edx-django-utils.readthedocs.io/en/latest/
    :alt: Documentation

.. |pyversions-badge| image:: https://img.shields.io/pypi/pyversions/edx-django-utils.svg
    :target: https://pypi.python.org/pypi/edx-django-utils/
    :alt: Supported Python versions

.. |license-badge| image:: https://img.shields.io/github/license/edx/edx-django-utils.svg
    :target: https://github.com/edx/edx-django-utils/blob/master/LICENSE.txt
    :alt: License
