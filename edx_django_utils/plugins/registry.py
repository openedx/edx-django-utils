"""
Code to create Registry of django app plugins
"""
from .plugin_manager import PluginManager
import six


class DjangoAppRegistry(PluginManager):
    """
    DjangoAppRegistry is a registry of django app plugins.
    """

    pass


def get_app_configs(project_type):
    return six.itervalues(DjangoAppRegistry.get_available_plugins(project_type))
