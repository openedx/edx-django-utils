Django App Plugins
==================

.. contents::
   :local:
   :depth: 2

Overview
--------

Provides functionality to enable improved plugin support of Django apps.

This can be used to extend any service with code that is not core to the service,
but will become discoverable by that service for an individual deployment.

Once a Django project is enhanced with this functionality, any participating
Django app (a.k.a. Plugin App) that is PIP-installed on the system is
automatically included in the Django project's INSTALLED_APPS list. In addition,
the participating Django app's URLs and Settings are automatically recognized by
the Django project. Furthermore, the Plugin Signals feature allows Plugin Apps
to shift their dependencies on Django Signal Senders from code-time to runtime.

While Django+Python already support dynamic installation of components/apps,
they do not have out-of-the-box support for plugin apps that auto-install
into a containing Django project.

.. _decision (ADR) for moving this to edx-django-utils: https://github.com/openedx/edx-django-utils/blob/master/docs/decisions/0002-extract-plugins-infrastructure-from-edx-platform.rst

Enable Plugins in an IDA
------------------------

.. note:: Enabling plugins only needs to have once per IDA. If you are creating a plugin app for an IDA that already supports plugins, skip this section. If you are unsure, see the how-to for details.

See `instructions to enable plugins for an IDA`_.

.. _instructions to enable plugins for an IDA: https://github.com/openedx/edx-django-utils/blob/master/edx_django_utils/plugins/docs/how_tos/how_to_enable_plugins_for_an_ida.rst

# TODO: 1. Add a version of the above note about "once per IDA" to the top of the how-to, and include a section about how to quickly tell if the IDA already supports plugins or not.

Creating a Plugin App
---------------------

.. note:: Do not use this plugin framework for required apps. In this case, clarity can come from explicitly using ``INSTALLED_APPS`` rather than this plugin framework.

# TODO: Move the sections below to a separate how_to_create_a_plugin_app.rst. Repeat the note about "required apps" in the how-to.

.. 

   .. note:: Do not use this plugin framework for required apps. In this case, clarity can come from explicitly using ``INSTALLED_APPS`` rather than this plugin framework.

   Using edx-cookiecutter
   ^^^^^^^^^^^^^^^^^^^^^^
   The simplest way to create a new plugin for edx-platform is to use the edx-cookiecutter tool. After creating a new repository, follow the instructions for cookiecutter-django-app. This will allow you to skip step 1 below, as the cookie cutter will create a skeleton App Config for you.

   Manual setup
   ^^^^^^^^^^^^

   In order to make use of the edx_django_utils/plugin functionality, new plugin apps need to:

   1. create an AppConfig class in their apps module, as described in Django's
   `Application Configuration <https://docs.djangoproject.com/en/2.0/ref/applications/#django.apps.AppConfig>`_.

   2. add their AppConfig class to the appropriate entry point in their setup.py
   file::

       from setuptools import setup
       setup(
           ...
           entry_points={
               "lms.djangoapp": [
                   "my_app = full_python_path.my_app.apps:MyAppConfig",
               ],
               "cms.djangoapp": [
               ],
           }
       )

   3. (optional, but recommended) Create a top-level settings/ directory with common.py and production.py modules. This will allow you to use the PluginSettings.CONFIG option as written below.

   4. configure the Plugin App in their AppConfig
   class::

       from django.apps import AppConfig
       from edx_django_utils.plugins.constants import (
           ProjectType, SettingsType, PluginURLs, PluginSettings, PluginContexts
       )
       class MyAppConfig(AppConfig):
           name = 'full_python_path.my_app'

           # Class attribute that configures and enables this app as a Plugin App.
           plugin_app = {

               # Configuration setting for Plugin URLs for this app.
               PluginURLs.CONFIG: {

                   # Configure the Plugin URLs for each project type, as needed.
                   ProjectType.LMS: {

                       # The namespace to provide to django's urls.include.
                       PluginURLs.NAMESPACE: 'my_app',

                       # The application namespace to provide to django's urls.include.
                       # Optional; Defaults to None.
                       PluginURLs.APP_NAME: 'my_app',

                       # The regex to provide to django's urls.url.
                       # Optional; Defaults to r''.
                       PluginURLs.REGEX: r'^api/my_app/',

                       # The python path (relative to this app) to the URLs module to be plugged into the project.
                       # Optional; Defaults to 'urls'.
                       PluginURLs.RELATIVE_PATH: 'api.urls',
                   }
               },

               # Configuration setting for Plugin Settings for this app. 
               PluginSettings.CONFIG: {

                   # Configure the Plugin Settings for each Project Type, as needed.
                   ProjectType.LMS: {

                       # Configure each Settings Type, as needed.
                       SettingsType.PRODUCTION: {

                           # The python path (relative to this app) to the settings module for the relevant Project Type and Settings Type.
                           # Optional; Defaults to 'settings'.
                           PluginSettings.RELATIVE_PATH: 'settings.production',
                       },
                       SettingsType.COMMON: {
                           PluginSettings.RELATIVE_PATH: 'settings.common',
                       },
                   }
               },

               # Configuration setting for Plugin Signals for this app.
               PluginSignals.CONFIG: {

                   # Configure the Plugin Signals for each Project Type, as needed.
                   ProjectType.LMS: {

                       # The python path (relative to this app) to the Signals module containing this app's Signal receivers.
                       # Optional; Defaults to 'signals'.
                       PluginSignals.RELATIVE_PATH: 'my_signals',

                       # List of all plugin Signal receivers for this app and project type.
                       PluginSignals.RECEIVERS: [{

                           # The name of the app's signal receiver function.
                           PluginSignals.RECEIVER_FUNC_NAME: 'on_signal_x',

                           # The full path to the module where the signal is defined.
                           PluginSignals.SIGNAL_PATH: 'full_path_to_signal_x_module.SignalX',

                           # The value for dispatch_uid to pass to Signal.connect to prevent duplicate signals.
                           # Optional; Defaults to full path to the signal's receiver function.
                           PluginSignals.DISPATCH_UID: 'my_app.my_signals.on_signal_x',

                           # The full path to a sender (if connecting to a specific sender) to be passed to Signal.connect.
                           # Optional; Defaults to None.
                           PluginSignals.SENDER_PATH: 'full_path_to_sender_app.ModelZ',
                       }],
                   }
               },

               # Configuration setting for Plugin Contexts for this app.
               PluginContexts.CONFIG: {

                   # Configure the Plugin Signals for each Project Type, as needed.
                   ProjectType.LMS: {

                       # Key is the view that the app wishes to add context to and the value
                       # is the function within the app that will return additional context
                       # when called with the original context
                       'course_dashboard': 'my_app.context_api.get_dashboard_context'
                   }
               }
           }

   OR use string constants when they cannot import from djangoapps.plugins::

       from django.apps import AppConfig
       class MyAppConfig(AppConfig):
           name = 'full_python_path.my_app'

           plugin_app = {
               'url_config': {
                   'lms.djangoapp': {
                       'namespace': 'my_app',
                       'regex': '^api/my_app/',
                       'relative_path': 'api.urls',
                   }
               },
               'settings_config': {
                   'lms.djangoapp': {
                       'production': { 'relative_path': 'settings.production' },
                       'common': { 'relative_path': 'settings.common' },
                   }
               },
               'signals_config': {
                   'lms.djangoapp': {
                       'relative_path': 'my_signals',
                       'receivers': [{
                           'receiver_func_name': 'on_signal_x',
                           'signal_path': 'full_path_to_signal_x_module.SignalX',
                           'dispatch_uid': 'my_app.my_signals.on_signal_x',
                           'sender_path': 'full_path_to_sender_app.ModelZ',
                       }],
                   }
               },
               'view_context_config': {
                   'lms.djangoapp': {
                       'course_dashboard': 'my_app.context_api.get_dashboard_context'
                   }
               }
           }

   5. For Plugin Settings, insert the following function into each of the Plugin
   Settings modules that you created in the /settings folder::

       def plugin_settings(settings):
           # Update the provided settings module with any app-specific settings.
           # For example:
           #     settings.FEATURES['ENABLE_MY_APP'] = True
           #     settings.MY_APP_POLICY = 'foo'

   Local Testing
   ^^^^^^^^^^^^^
   To test your plugin locally with edx-platform, exec into a running lms or cms container and run ``make requirements`` followed by ``pip install git+https://github.com/me/myrepo@mybranch``. 

   Then, open a shell using ``./manage.py lms shell`` and run::

   >>> from django.apps import apps
   >>> [app.verbose_name for app in apps.get_app_configs()]

   You should see your app in the printed output.

   Another easy way to test if your plugin is installed correctly is to create a simple management command within your plugin. If the plugin is installed correctly into edx-platform, you should be able to run this management command from within the lms or cms container.

Design Principles
-----------------

This Django App Plugin functionality allows for Django-framework code to be
encapsulated within each Django app, rather than having a monolith Project that
is aware of the details of its Django apps. It is motivated by the following
design principles:

* Single Responsibility Principle, which says "a class or module should have
  one, and only one, reason to change." When code related to a single Django app
  changes, there's no reason for its containing project to also change. The
  encapsulation and modularity resulting from code being co-located with its
  owning Django app helps prevent "God objects" that have too much responsibility
  and knowledge of the details.

* Open Closed Principle, which says "software entities should be open for
  extension, but closed for modification." IDAs are extensible via
  installation of Django apps. Having automatic Django App Plugin support allows
  for this extensibility without modification to an IDA. Currently, this is only
  set up in edx platform. Going forward, we expect this capability to be widely
  used by othe IDAs to enable enchancement without need to modify core IDA code.

* Dependency Inversion Principle, which says "high level modules should not
  depend upon low level modules." The high-level module here is the Django
  project, while the participating Django app is the low-level module. For
  long-term maintenance of a system, dependencies should go from low-level
  modules/details to higher level ones.
