"""
Tests for the code_owner monitoring middleware
"""
import timeit
from unittest import TestCase

import ddt
from django.test import override_settings
from mock import patch

from edx_django_utils.monitoring import get_code_owner_from_module
from edx_django_utils.monitoring.internal.code_owner.utils import clear_cached_mappings


@ddt.ddt
class MonitoringUtilsTests(TestCase):
    """
    Tests for the code_owner monitoring utility functions
    """
    def setUp(self):
        super().setUp()
        clear_cached_mappings()

    @override_settings(CODE_OWNER_MAPPINGS={
        'team-red': [
            'openedx.core.djangoapps.xblock',
            'lms.djangoapps.grades',
        ],
        'team-blue': [
            'common.djangoapps.xblock_django',
        ],
    })
    @ddt.data(
        ('xbl', None),
        ('xblock_2', None),
        ('xblock', 'team-red'),
        ('openedx.core.djangoapps', None),
        ('openedx.core.djangoapps.xblock', 'team-red'),
        ('openedx.core.djangoapps.xblock.views', 'team-red'),
        ('grades', 'team-red'),
        ('lms.djangoapps.grades', 'team-red'),
        ('xblock_django', 'team-blue'),
        ('common.djangoapps.xblock_django', 'team-blue'),
    )
    @ddt.unpack
    def test_code_owner_mapping_hits_and_misses(self, module, expected_owner):
        actual_owner = get_code_owner_from_module(module)
        self.assertEqual(expected_owner, actual_owner)

    @override_settings(CODE_OWNER_MAPPINGS=['invalid_setting_as_list'])
    @patch('edx_django_utils.monitoring.internal.code_owner.utils.log')
    def test_code_owner_mapping_with_invalid_dict(self, mock_logger):
        with self.assertRaises(AssertionError):
            get_code_owner_from_module('xblock')
            mock_logger.exception.assert_called_with(
                'Error processing code_owner_mappings.',
            )

    def test_code_owner_mapping_with_no_settings(self):
        self.assertIsNone(get_code_owner_from_module('xblock'))

    def test_mapping_performance(self):
        code_owner_mappings = {
            'team-red': []
        }
        # create a long list of mappings that are nearly identical
        for n in range(1, 200):
            path = 'openedx.core.djangoapps.{}'.format(n)
            code_owner_mappings['team-red'].append(path)
        with override_settings(CODE_OWNER_MAPPINGS=code_owner_mappings):
            call_iterations = 100
            time = timeit.timeit(
                # test a module name that matches nearly to the end, but doesn't actually match
                lambda: get_code_owner_from_module('openedx.core.djangoapps.XXX.views'), number=call_iterations
            )
            average_time = time / call_iterations
            self.assertLess(average_time, 0.0005, 'Mapping takes {}s which is too slow.'.format(average_time))
