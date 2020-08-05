"""
Adds support for first class plugins that can be added to the edX platform.
"""

import collections
import functools


from collections import OrderedDict

from stevedore.extension import ExtensionManager


class PluginError(Exception):
    """
    Base Exception for when an error was found regarding plugins.
    """


class PluginManager:
    """
    Base class that manages plugins for the edX platform.
    """

    @classmethod
    @functools.lru_cache(maxsize=None)
    def get_available_plugins(cls, namespace=None):
        """
        Returns a dict of all the plugins that have been made available through the platform.
        """
        # Note: we're creating the extension manager lazily to ensure that the Python path
        # has been correctly set up. Trying to create this statically will fail, unfortunately.
        plugins = OrderedDict()
        extension_manager = ExtensionManager(
            namespace=namespace or cls.NAMESPACE
        )  # pylint: disable=no-member
        for plugin_name in extension_manager.names():
            plugins[plugin_name] = extension_manager[plugin_name].plugin
        return plugins

    @classmethod
    def get_plugin(cls, name, namespace=None):
        """
        Returns the plugin with the given name.
        """
        plugins = cls.get_available_plugins(namespace)
        if name not in plugins:
            raise PluginError(
                u"No such plugin {name} for entry point {namespace}".format(
                    name=name,
                    namespace=namespace or cls.NAMESPACE,  # pylint: disable=no-member
                )
            )
        return plugins[name]
