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

Enable Plugins in an IDA
------------------------

See :doc:`instructions to enable plugins for an IDA <docs/how_tos/how_to_enable_plugins_for_an_ida>`.

Creating a Plugin App
---------------------

See :doc:`how to create a plugin app <docs/how_tos/how_to_create_a_plugin_app>`.

.. note:: Do not use this plugin framework for required apps. Instead, explicitly add your required app to the ``INSTALLED_APPS`` of the IDA.

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
  used by other IDAs to enable enhancement without need to modify core IDA code.

* Dependency Inversion Principle, which says "high level modules should not
  depend upon low level modules." The high-level module here is the Django
  project, while the participating Django app is the low-level module. For
  long-term maintenance of a system, dependencies should go from low-level
  modules/details to higher level ones.
