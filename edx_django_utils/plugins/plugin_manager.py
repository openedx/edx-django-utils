"""
Adds support for first class plugins that can be added to the edX platform.
"""

import collections
import functools


from collections import OrderedDict

from stevedore.extension import ExtensionManager


class process_cached():  # pylint: disable=invalid-name
    """
    Decorator to cache the result of a function for the life of a process.
    If the return value of the function for the provided arguments has not
    yet been cached, the function will be calculated and cached. If called
    later with the same arguments, the cached value is returned
    (not reevaluated).
    https://wiki.python.org/moin/PythonDecoratorLibrary#Memoize
    WARNING: Only use this process_cached decorator for caching data that
    is constant throughout the lifetime of a gunicorn worker process,
    is costly to compute, and is required often.  Otherwise, it can lead to
    unwanted memory leakage.
    """

    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        if not isinstance(args, collections.Hashable):
            # uncacheable. a list, for instance.
            # better to not cache than blow up.
            return self.func(*args)
        if args in self.cache:
            return self.cache[args]
        else:
            value = self.func(*args)
            self.cache[args] = value
            return value

    def __repr__(self):
        """
        Return the function's docstring.
        """
        return self.func.__doc__

    def __get__(self, obj, objtype):
        """
        Support instance methods.
        """
        return functools.partial(self.__call__, obj)


class PluginError(Exception):
    """
    Base Exception for when an error was found regarding plugins.
    """


class PluginManager():
    """
    Base class that manages plugins for the edX platform.
    """
    @classmethod
    @process_cached
    def get_available_plugins(cls, namespace=None):
        """
        Returns a dict of all the plugins that have been made available through the platform.
        """
        # Note: we're creating the extension manager lazily to ensure that the Python path
        # has been correctly set up. Trying to create this statically will fail, unfortunately.
        plugins = OrderedDict()
        extension_manager = ExtensionManager(namespace=namespace or cls.NAMESPACE)  # pylint: disable=no-member
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
            raise PluginError(u"No such plugin {name} for entry point {namespace}".format(
                name=name,
                namespace=namespace or cls.NAMESPACE,  # pylint: disable=no-member
            ))
        return plugins[name]
