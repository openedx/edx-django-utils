How to enable plugins for an IDA
================================

Django Projects
---------------

In order to enable this functionality in a Django project, the project needs to
update:

1. its settings to extend its INSTALLED_APPS to include the Plugin Apps
::

   INSTALLED_APPS.extend(plugin_apps.get_plugin_apps(...))

2. its settings to add all Plugin Settings
::

   plugin_settings.add_plugins(__name__, ...)

3. its urls to add all Plugin URLs
::

   urlpatterns.extend(plugin_urls.get_plugin_url_patterns(...))

4. its setup to register PluginsConfig (for connecting Plugin Signals)
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
