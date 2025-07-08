"""
Utilities for working with Django storage backends.

This module provides helper functions to retrieve storage instances
based on Django's STORAGES setting, legacy configuration, or
fallback to the default storage.
"""

from django.conf import settings
from django.core.files.storage import default_storage, storages
from django.utils.module_loading import import_string


def get_named_storage(name=None, legacy_setting_name=None):
    """
    Returns an instance of the configured storage backend.

    This function prioritizes configuration in the following order:

    1. Use the named storage from Django's STORAGES if `name` is defined.
    2. If not found, check the legacy setting (if `legacy_setting_name` is provided).
    3. If still undefined, fall back to Django's default_storage.

    Args:
        name (str, optional): The name of the storage as defined in Django's STORAGES setting.
        legacy_setting_name (str, optional): The legacy setting dict to check
            for a storage class path and options.

    Returns:
        An instance of the configured storage backend.

    Raises:
        ValueError: If neither `name` nor `legacy_setting_name` are provided.
        ImportError: If the specified storage class cannot be imported.
    """
    if not name and not legacy_setting_name:
        raise ValueError("You must provide at least 'name' or 'legacy_setting_name'.")

    # 1. Check Django 4.2+ STORAGES dict if `name` is provided
    if name:
        storages_config = getattr(settings, 'STORAGES', {})
        if name in storages_config:
            return storages[name]

    # 2. Check legacy config if `legacy_setting_name` is provided
    if legacy_setting_name:
        legacy_config = getattr(settings, legacy_setting_name, {})
        storage_class_path = legacy_config.get('class') or legacy_config.get('STORAGE_CLASS')
        options = legacy_config.get('options', {}) or legacy_config.get('STORAGE_KWARGS', {})
        if storage_class_path:
            storage_class = import_string(storage_class_path)
            return storage_class(**options)

    # 3. Fallback to Django's default_storage
    return default_storage
