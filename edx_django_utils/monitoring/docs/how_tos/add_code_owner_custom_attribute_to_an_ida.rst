Add Code_Owner Custom Attributes to an IDA
==========================================

.. contents::
   :local:
   :depth: 2

What are the code owner custom attributes?
------------------------------------------

The code owner custom attributes can be used to create custom dashboards and alerts for monitoring the things that you own. It was originally introduced for the LMS, as is described in this `ADR on monitoring by code owner`_.

The code owner custom attributes consist of:

* code_owner: The owner name. When themes and squads are used, this will be the theme and squad names joined by a hyphen.
* code_owner_theme: The theme name of the owner.
* code_owner_squad: The squad name of the owner. Use this to avoid issues when theme name changes.

You can now easily add this same attribute to any IDA so that your dashboards and alerts can work across multiple IDAs at once.

If you want to know about custom attributes in general, see :doc:`using_custom_attributes`.

.. _ADR on monitoring by code owner: https://github.com/edx/edx-platform/blob/master/lms/djangoapps/monitoring/docs/decisions/0001-monitoring-by-code-owner.rst

Setting up the Middleware
-------------------------

You simply need to add ``edx_django_utils.monitoring.CodeOwnerMonitoringMiddleware`` as described in the README to make this functionality available. Then it is ready to be configured.

Handling celery tasks
---------------------

Celery tasks require use of a special decorator to set the ``code_owner`` custom attributes because no middleware will be run.

Here is an example::

  @task()
  @set_code_owner_attribute
  def example_task():
      ...

If the task is not compatible with additional decorators, you can use the following alternative::

  @task()
  def example_task():
      set_code_owner_attribute_from_module(__name__)
      ...

An untested potential alternative to the decorator is documented in the `Code Owner for Celery Tasks ADR`_, should we run into maintenance issues using the decorator.

.. _Code Owner for Celery Tasks ADR: https://github.com/edx/edx-platform/blob/master/lms/djangoapps/monitoring/docs/decisions/0003-code-owner-for-celery-tasks.rst

Configuring your app settings
-----------------------------

Once the Middleware is made available, simply set the Django Settings ``CODE_OWNER_MAPPINGS`` and ``CODE_OWNER_THEMES`` appropriately.

The following example shows how you can include an optional config for a catch-all using ``'*'``. Although you might expect this example to use Python, it is intentionally illustrated in YAML because the catch-all requires special care in YAML.

::

    # YAML format of example CODE_OWNER_MAPPINGS
    CODE_OWNER_MAPPINGS:
      theme-x-team-red:
        - xblock_django
        - openedx.core.djangoapps.xblock
      theme-x-team-blue:
      - '*'  # IMPORTANT: you must surround * with quotes in yml

    # YAML format of example CODE_OWNER_THEMES
    CODE_OWNER_THEMES:
      theme-x:
      - theme-x-team-red
      - theme-x-team-blue

How to find and fix code_owner mappings
---------------------------------------

If you are missing the ``code_owner`` custom attributes on a particular Transaction or Error, or if ``code_owner`` is matching the catch-all, but you want to add a more specific mapping, you can use the other `code_owner supporting attributes`_ to determine what the appropriate mappings should be.

.. _code_owner supporting attributes: https://github.com/edx/edx-django-utils/blob/c022565/edx_django_utils/monitoring/internal/code_owner/middleware.py#L30-L34

Updating New Relic monitoring
-----------------------------

NRQL (New Relic Query Language) that uses the ``code_owner`` custom attributes (e.g. ``code_owner_squad``, ``code_owner_theme``, or ``code_owner``) may be found in alert conditions or dashboards.

To change a squad or theme name, you should *expand* the NRQL before the change, and *contract* the NRQL after the change.

Note: For edx.org, it is useful to wait a month before contracting the monitoring.

Example expand phase NRQL::

    code_owner_squad IN ('old-squad-name', 'new-squad-name')
    code_owner_theme IN ('old-theme-name', 'new-theme-name')

Example contract phase NRQL::

    code_owner_squad = 'new-squad-name'
    code_owner_theme = 'new-theme-name'

To find the relevant NRQL to update, see `Searching New Relic NRQL`_.

Searching New Relic NRQL
------------------------

The search script new_relic_nrql_search.py is generally useful for searching NRQL (New Relic Query Language) in New Relic. It searches the NRQL in New Relic alert policies (static alert conditions only), and in New Relic dashboards. Use ``--help`` for more details.

The script can be especially useful for helping with the expand/contract phase when changing squad or theme names. For example, you could use the following::

    new_relic_nrql_search.py --regex old-squad-name
    new_relic_nrql_search.py --regex new-squad-name
