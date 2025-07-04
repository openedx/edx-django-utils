"""
Utilities for working with Django storage backends.

This module provides helper functions to retrieve storage instances
based on Django's STORAGES setting, legacy configuration, or
fallback to the default storage.
"""

from django.conf import settings
from django.core.files.storage import default_storage, storages
from django.utils.module_loading import import_string


def get_named_storage(name, legacy_setting_name=None):
    """
    Returns an instance of the configured storage backend for the given name.

    This function prioritizes different settings in the following order to determine
    which storage class to use:

    1. Use the named storage from Django's STORAGES if defined (Django 4.2+).
    2. If not available, check the legacy setting (if provided).
    3. If still undefined, fall back to Django's default_storage.

    Args:
        name (str): The name of the storage as defined in Django's STORAGES setting.
        legacy_setting_name (str, optional): The name of the legacy setting dict
            to check for a storage class path and options.

    Returns:
        An instance of the configured storage backend.

    Raises:
        ImportError: If the specified storage class cannot be imported.
    """
    # 1. Check Django 4.2+ STORAGES dict
    storages_config = getattr(settings, 'STORAGES', {})
    if name in storages_config:
        return storages[name]

    # 2. Check legacy config
    if legacy_setting_name:
        legacy_config = getattr(settings, legacy_setting_name, {})
        storage_class_path = legacy_config.get('class')
        options = legacy_config.get('options', {})
        if storage_class_path:
            storage_class = import_string(storage_class_path)
            return storage_class(**options)

    # 3. Fallback to Django's default_storage
    return default_storage
