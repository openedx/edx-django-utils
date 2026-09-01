Update Monitoring for Squad or Theme Changes
============================================

.. contents::
   :local:
   :depth: 2

Understanding code owner custom attributes
------------------------------------------

If you first need some background on the ``code_owner_squad`` and ``code_owner_theme`` custom attributes, see :doc:`add_code_owner_custom_attribute_to_an_ida`.

Expand and contract name changes
--------------------------------

NRQL (New Relic Query Language) statements that use the ``code_owner_squad`` or ``code_owner_theme`` (or ``code_owner``) custom attributes may be found in alert conditions or dashboards.

To change a squad or theme name, you should *expand* the NRQL before the change, and *contract* the NRQL after the change.

.. note::

    For edx.org, it is useful to wait a month before implementing the contract phase of the monitoring update.

Example expand phase NRQL::

    code_owner_squad IN ('old-squad-name', 'new-squad-name')
    code_owner_theme IN ('old-theme-name', 'new-theme-name')

Example contract phase NRQL::

    code_owner_squad = 'new-squad-name'
    code_owner_theme = 'new-theme-name'
