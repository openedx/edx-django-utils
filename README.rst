edx-django-utils
================

|pypi-badge| |ci-badge| |codecov-badge| |doc-badge| |pyversions-badge|
|license-badge| |status-badge|

EdX utilities for Django Application development.

Note that some utilities may warrant their own repository. A judgement call
needs to be made as to whether code properly belongs here or not. Please
review with the Architecture Team if you have any questions.

Purpose
-------

This repository includes shared utilities for:

* `Cache Utilities`_: Includes a RequestCache and a TieredCache.

* `Django User and Group Utilities`_: Includes user and group utilities.

* `IP Address Utilities`_: Utilities for handling request IP addresses.

* `Logging Utilities`_: Includes log filters and an encrypted logging helper.

* `Monitoring Utilities`_: Includes Middleware and utilities for enhanced monitoring.
  At this time, supports NewRelic monitoring.

* `Plugin Infrastructure`_: Enables enhanced Django Plugin capabilities.

* `Security Utilities`_: Includes a middleware to add CSP response headers.

* `Data Generation`_: Management command for generating Django data based on model factories.

.. _Cache Utilities: edx_django_utils/cache/README.rst

.. _Django User and Group Utilities: edx_django_utils/user/README.rst

.. _IP Address Utilities: edx_django_utils/ip/README.rst

.. _Logging Utilities: edx_django_utils/logging/README.rst

.. _Monitoring Utilities: edx_django_utils/monitoring/README.rst

.. _Plugin Infrastructure: edx_django_utils/plugins/README.rst

.. _Security Utilities: edx_django_utils/security/README.rst

.. _Data Generation: edx_django_utils/data_generation/README.rst

Documentation
-------------

The full documentation is in the docs directory, and is published to https://edx-django-utils.readthedocs.org.

Getting Started with Development
--------------------------------

Please see the Open edX documentation for `guidance on Python development <https://docs.openedx.org/en/latest/developers/how-tos/get-ready-for-python-dev.html>`_ in this repo.

Design Pattern followed by packages
-----------------------------------

All tools in edx_django_utils should expose their public api in their __init__.py files. This entails adding to __init__.py all functions/classes/constants/objects that are intended to be used by users of library.

Getting Help
------------

If you're having trouble, we have discussion forums at
`discuss.openedx.org <https://discuss.openedx.org>`_ where you can connect with others in the
community.

Our real-time conversations are on Slack. You can request a `Slack
invitation`_, then join our `community Slack workspace`_.

For anything non-trivial, the best path is to `open an issue`__ in this
repository with as many details about the issue you are facing as you
can provide.

__ https://github.com/openedx/django-config-models/issues

For more information about these options, see the `Getting Help`_ page.

.. _Slack invitation: https://openedx.org/slack
.. _community Slack workspace: https://openedx.slack.com/
.. _Getting Help: https://openedx.org/getting-help

How To Contribute
-----------------

Contributions are very welcome.

Please read `How To Contribute <https://github.com/openedx/.github/blob/master/CONTRIBUTING.md>`_ for details.

PR description template should be automatically applied if you are sending PR from github interface; otherwise you
can find it it at `PULL_REQUEST_TEMPLATE.md <https://github.com/openedx/edx-django-utils/blob/master/.github/PULL_REQUEST_TEMPLATE.md>`_

Issue report template should be automatically applied if you are sending it from github UI as well; otherwise you
can find it at `ISSUE_TEMPLATE.md <https://github.com/openedx/edx-django-utils/blob/master/.github/ISSUE_TEMPLATE.md>`_

This project is currently accepting all types of contributions, bug fixes, security fixes, maintenance work, or new features. However, please make sure to have a discussion about your new feature idea with the maintainers prior to beginning development to maximize the chances of your change being accepted. You can start a conversation by creating a new issue on this repo summarizing your idea.

Open edX Code of Conduct
------------------------
All community members are expected to follow the `Open edX Code of Conduct`_.

.. _Open edX Code of Conduct: https://openedx.org/code-of-conduct/

People
------
The assigned maintainers for this component and other project details may be
found in `Backstage`_. Backstage pulls this data from the ``catalog-info.yaml``
file in this repo.


.. _Backstage: https://backstage.openedx.org/catalog/default/component/edx-django-utils

Reporting Security Issues
-------------------------

Please do not report security issues in public. Please email security@openedx.org.

License
-------

The code in this repository is licensed under the Apache License, Version 2.0, unless
otherwise noted.

Please see ``LICENSE.txt`` for details.


.. |pypi-badge| image:: https://img.shields.io/pypi/v/edx-django-utils.svg
    :target: https://pypi.python.org/pypi/edx-django-utils/
    :alt: PyPI

.. |ci-badge| image:: https://github.com/openedx/edx-django-utils/workflows/Python%20CI/badge.svg?branch=master
    :target: https://github.com/openedx/edx-django-utils/actions?query=workflow%3A%22Python+CI%22
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
    :target: https://github.com/openedx/edx-django-utils/blob/master/LICENSE.txt
    :alt: License

.. |status-badge| image:: https://img.shields.io/badge/Status-Maintained-brightgreen
    :alt: Maintenance status
