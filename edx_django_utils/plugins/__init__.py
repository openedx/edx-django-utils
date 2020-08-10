"""
Plugins infrastructure

See README.rst for details.
"""

from .constants import PluginContexts, PluginSettings, PluginSignals, PluginURLs
from .plugin_apps import get_apps
from .plugin_contexts import get_plugins_view_context
from .plugin_manager import PluginError, PluginManager
from .plugin_settings import add_plugins
from .plugin_signals import connect_receivers
from .plugin_urls import get_patterns, get_url
from .registry import get_app_configs
