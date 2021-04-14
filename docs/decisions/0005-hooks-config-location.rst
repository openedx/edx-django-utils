Configuration for filters in the Hooks Extension Framework
==========================================================

Status
------

Draft

Context
-------

Context taken from the Discuss thread `Configuration for the Hooks Extension Framework <https://discuss.openedx.org/t/configuration-for-the-hooks-extension-framework/4527>`_

We need a way to configure a list of functions (filters) that will be called at different places (triggers) in the code of edx-platform.

So, for a string like:

"openedx.lms.auth.pre_register.filter.v1"

We need to define a list of functions:

.. code-block:: python

    [
        "from_a_plugin.filters.filter_1",
        "from_a_plugin.filters.filter_n",
        "from_some_other_package.filters.filter_1",
        # ... and so.
    ]


We have considered two alternatives:

* A dict in the Django settings.
    * Advantages:
        * It is very standard, everyone should know how to change it by now.
        * Can be altered without installing plugins.
    * Disadvantages:
        * It is hard to document a large dict.
        * Could grow into something difficult to manage.

* In a view of the AppConfig of your plugin.
    * Advantages:
        * Each plugin can extend the config to add its own filters without collisions.
    * Disadvantages:
        * It’s not possible to control the ordering of different filters being connected to the same trigger by different plugins.
        * For updates, an operator must install a new version of the dependency which usually is longer and more difficult than changing vars and restart.
        * Not easy to configure by tenant if you use site configs.
        * Requires a plugin.

Decision
--------

We decided to use a dictionary with a flexible format defined using Django settings.

Consequences
------------

1. The only way to configure Hooks Extension Framework is via Django settings using one of these three formats:

**Option 1**: this is the more detailed option and from it, the others can be derived. Through this configuration can be configured the list of functions to be executed.
to execute them.

.. code-block:: python

    HOOKS_EXTENSION_CONFIG = {
        "openedx.service.trigger_context.location.trigger_type.vi": {
            "pipeline": [
                "from_a_plugin.filters.filter_1",
                "from_a_plugin.filters.filter_n",
                "from_some_other_package.filters.filter_1",
            ],
        }
    }

**Option 2**: this option only considers the configuration of the list of functions to be executed.

.. code-block:: python

    HOOKS_EXTENSION_CONFIG = {
        "openedx.service.trigger_context.location.trigger_type.vi": {
            [
                "from_a_plugin.filters.filter_1",
                "from_a_plugin.filters.filter_n",
                "from_some_other_package.filters.filter_1",
            ],
        }
    }

**Option 3**: this option considers that there's just one function to be executed.

.. code-block:: python

    HOOKS_EXTENSION_CONFIG = {
        "openedx.service.trigger_context.location.trigger_type.vi": "from_a_plugin.filters.filter_1",
    }

2. Given that Site Configurations is not available in this repository, it can't be used to configure hooks.
