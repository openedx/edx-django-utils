"""
Unit tests for storage utilities in edx_django_utils.
"""

import ddt
from django.conf import settings
from django.core.files.storage import default_storage
from django.test import TestCase
from django.test.utils import override_settings

from edx_django_utils.storage.utils import get_named_storage


@ddt.ddt
class TestGetNamedStorage(TestCase):
    """
    Tests for the get_named_storage utility.
    """

    @ddt.data(
        (
            'avatars',
            'AVATAR_BACKEND',
            (
                {'avatars': {
                    'BACKEND': 'django.core.files.storage.FileSystemStorage',
                    'OPTIONS': {'location': '/tmp/avatars'}
                }},
                None  # No legacy config
            ),
            '/tmp/avatars'
        ),
        (
            'avatars',
            'AVATAR_BACKEND',
            (
                {},  # Empty STORAGES dict
                {
                    'class': 'django.core.files.storage.FileSystemStorage',
                    'options': {'location': '/tmp/legacy_avatars'}
                }
            ),
            '/tmp/legacy_avatars'
        ),
        (
            'certificates',
            'CERTIFICATE_BACKEND',
            (
                {'certificates': {
                    'BACKEND': 'django.core.files.storage.FileSystemStorage',
                    'OPTIONS': {'location': '/tmp/certificates'}
                }},
                None
            ),
            '/tmp/certificates'
        ),
        (
            'certificates',
            'CERTIFICATE_BACKEND',
            (
                {},  # Empty STORAGES dict
                {
                    'class': 'django.core.files.storage.FileSystemStorage',
                    'options': {'location': '/tmp/legacy_certificates'}
                }
            ),
            '/tmp/legacy_certificates'
        ),
    )
    @ddt.unpack
    def test_get_named_storage(self, storage_name, legacy_setting_name, config, expected_location):
        """
        Test get_named_storage with both STORAGES dict and legacy config.
        """
        storages_config, legacy_config = config

        with override_settings(STORAGES=storages_config or {}):
            if legacy_config:
                setattr(settings, legacy_setting_name, legacy_config)
            elif hasattr(settings, legacy_setting_name):
                delattr(settings, legacy_setting_name)

            storage = get_named_storage(storage_name, legacy_setting_name=legacy_setting_name)
            self.assertEqual(storage.location, expected_location)

    def test_fallback_to_default_storage(self):
        """
        Test fallback to default_storage when neither STORAGES dict nor legacy config is defined.
        """
        with override_settings(STORAGES={
            'default': {
                'BACKEND': 'django.core.files.storage.FileSystemStorage',
                'OPTIONS': {'location': '/tmp/default'}
            }
        }):
            for legacy_setting in ['AVATAR_BACKEND', 'CERTIFICATE_BACKEND', 'PROFILE_IMAGE_BACKEND']:
                if hasattr(settings, legacy_setting):
                    delattr(settings, legacy_setting)

            for storage_name, legacy_setting_name in [
                ('avatars', 'AVATAR_BACKEND'),
                ('certificates', 'CERTIFICATE_BACKEND'),
                ('profile_image', 'PROFILE_IMAGE_BACKEND'),
            ]:
                storage = get_named_storage(storage_name, legacy_setting_name=legacy_setting_name)
                self.assertEqual(storage, default_storage)
