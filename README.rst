edx-django-utils
================

|pypi-badge| |ci-badge| |codecov-badge| |doc-badge| |pyversions-badge|
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

* `Django User and Group Utilities`_: Includes user and group utilities.

.. _Cache Utilities: edx_django_utils/cache/README.rst

.. _Monitoring Utilities: edx_django_utils/monitoring/README.rst

.. _Plugin Infrastructure: edx_django_utils/plugins/README.rst

.. _Django User and Group Utilities: edx_django_utils/user/README.rst

Documentation
-------------

The full documentation is in the docs directory.

TODO: Publish to https://edx-django-utils.readthedocs.org.

Development Workflow
--------------------

One Time Setup
______________
.. code-block::

  # clone the repo
  git clone git@github.com:edx/edx-django-utils.git
  cd edx-django-utils

  # setup a virtualenv using virtualenvwrapper with the same name as the repo and activate it.
  # $(basename $(pwd)) will give you the name of the current working directory, in this case ``edx-django-utils``
  mkvirtualenv -p python3 $(basename $(pwd))


Every time you develop something in this repo
_____________________________________________
.. code-block::

  # Activate the virtualenv.
  workon edx-django-utils

  # Grab the latest code.
  git checkout master
  git pull

  # Install the dev requirements
  make requirements

  # Run the tests
  make test

  # Make a new branch for your changes
  git checkout -b <your_github_username>/<short_description>

  # Using your favorite editor, edit the code to make your change.
  vim …

  # Run your new tests
  pytest ./path/to/new/tests

  # Run all the test
  make test

  # Commit all your changes
  git commit …
  git push

  # Open a PR and ask for review.

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

.. |ci-badge| image:: https://github.com/edx/edx-django-utils/workflows/Python%20CI/badge.svg?branch=master
    :target: https://github.com/edx/edx-django-utils/actions?query=workflow%3A%22Python+CI%22
    :alt: CI

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
