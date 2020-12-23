How to enable plugins for an IDA
================================

Django Projects
---------------

In order to enable this functionality in a Django project, the project needs to
update:

1. its settings to extend its INSTALLED_APPS to include the Plugin Apps
::

   INSTALLED_APPS.extend(get_plugin_apps(...))

2. its settings to add all Plugin Settings
::

   add_plugins(__name__, ...)

3. its urls to add all Plugin URLs
::

   urlpatterns.extend(get_plugin_url_patterns(...))

4. its setup to register PluginsConfig (for connecting Plugin Signals)

.. note:: For a plugin that will appear in a single IDA, you could create constants like `ProjectType found in edx-platform`_. If the plugin is for many IDAs, we need to add a capability to this library with a global constant.

::

    from setuptools import setup
    setup(
        ...
        entry_points={
            "lms.djangoapp": [
                "plugins = openedx.core.djangoapps.plugins.apps:PluginsConfig",
            ],
            "cms.djangoapp": [
                "plugins = openedx.core.djangoapps.plugins.apps:PluginsConfig",
            ],
        }
    )

.. _ProjectType found in edx-platform: https://github.com/edx/edx-platform/blob/dbe40dae1a8b50fea0954e85f76ebf244129186e/openedx/core/djangoapps/plugins/constants.py#L14-L22
