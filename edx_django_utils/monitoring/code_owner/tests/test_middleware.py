"""
Tests for the code_owner monitoring middleware
"""
from unittest import TestCase
from unittest.mock import ANY

import ddt
from django.conf.urls import url
from django.test import RequestFactory, override_settings
from django.views.generic import View
from mock import Mock, call, patch

from edx_django_utils.monitoring.code_owner.middleware import CodeOwnerMetricMiddleware
from edx_django_utils.monitoring.code_owner.tests.mock_views import MockViewTest
from edx_django_utils.monitoring.code_owner.utils import _process_code_owner_mappings


class MockMiddlewareViewTest(View):
    pass


urlpatterns = [
    url(r'^middleware-test/$', MockMiddlewareViewTest.as_view()),
    url(r'^test/$', MockViewTest.as_view()),
]


@ddt.ddt
class CodeOwnerMetricMiddlewareTests(TestCase):
    """
    Tests for the code_owner monitoring utility functions
    """
    urls = 'lms.djangoapps.monitoring.tests.test_middleware.test_urls'

    def setUp(self):
        super().setUp()
        self.mock_get_response = Mock()
        self.middleware = CodeOwnerMetricMiddleware(self.mock_get_response)

    def test_init(self):
        self.assertEqual(self.middleware.get_response, self.mock_get_response)

    def test_request_call(self):
        self.mock_get_response.return_value = 'test-response'
        request = Mock()
        self.assertEqual(self.middleware(request), 'test-response')

    _REQUEST_PATH_TO_MODULE_PATH = {
        '/middleware-test/': 'edx_django_utils.monitoring.code_owner.tests.test_middleware',
        '/test/': 'edx_django_utils.monitoring.code_owner.tests.mock_views',
    }

    @override_settings(
        CODE_OWNER_MAPPINGS={'team-red': ['edx_django_utils.monitoring.code_owner.tests.mock_views']},
        ROOT_URLCONF=__name__,
    )
    @patch('edx_django_utils.monitoring.code_owner.middleware.set_custom_metric')
    @ddt.data(
        ('/middleware-test/', None),
        ('/test/', 'team-red'),
    )
    @ddt.unpack
    def test_code_owner_path_mapping_hits_and_misses(
        self, request_path, expected_owner, mock_set_custom_metric
    ):
        with patch(
                'edx_django_utils.monitoring.code_owner.utils._PATH_TO_CODE_OWNER_MAPPINGS',
                _process_code_owner_mappings()
        ):
            request = RequestFactory().get(request_path)
            self.middleware(request)
            expected_path_module = self._REQUEST_PATH_TO_MODULE_PATH[request_path]
            self._assert_code_owner_custom_metrics(
                mock_set_custom_metric, expected_code_owner=expected_owner, path_module=expected_path_module
            )

            mock_set_custom_metric.reset_mock()
            self.middleware.process_exception(request, None)
            self._assert_code_owner_custom_metrics(
                mock_set_custom_metric, expected_code_owner=expected_owner, path_module=expected_path_module
            )

    @override_settings(
        CODE_OWNER_MAPPINGS={'team-red': ['edx_django_utils.monitoring.code_owner.tests.mock_views']},
        ROOT_URLCONF=__name__,
    )
    @patch('edx_django_utils.monitoring.code_owner.middleware.set_custom_metric')
    @patch('newrelic.agent')
    @ddt.data(
        ('edx_django_utils.monitoring.code_owner.tests.test_middleware:MockMiddlewareViewTest', None),
        ('edx_django_utils.monitoring.code_owner.tests.mock_views:MockViewTest', 'team-red'),
    )
    @ddt.unpack
    def test_code_owner_transaction_mapping_hits_and_misses(
        self, transaction_name, expected_owner, mock_newrelic_agent, mock_set_custom_metric
    ):
        mock_newrelic_agent.current_transaction().name = transaction_name
        with patch(
                'edx_django_utils.monitoring.code_owner.utils._PATH_TO_CODE_OWNER_MAPPINGS',
                _process_code_owner_mappings()
        ):
            request = RequestFactory().get('/bad/path/')
            self.middleware(request)
            self._assert_code_owner_custom_metrics(
                mock_set_custom_metric, expected_code_owner=expected_owner, transaction_name=transaction_name
            )

            mock_set_custom_metric.reset_mock()
            self.middleware.process_exception(request, None)
            self._assert_code_owner_custom_metrics(
                mock_set_custom_metric, expected_code_owner=expected_owner, transaction_name=transaction_name
            )

    @override_settings(
        CODE_OWNER_MAPPINGS={'team-red': ['edx_django_utils.monitoring.code_owner.tests.mock_views']},
        ROOT_URLCONF=__name__,
    )
    @patch('edx_django_utils.monitoring.code_owner.middleware.set_custom_metric')
    @patch('newrelic.agent')
    def test_code_owner_transaction_mapping_error(self, mock_newrelic_agent, mock_set_custom_metric):
        mock_newrelic_agent.current_transaction = Mock(side_effect=Exception('forced exception'))
        with patch(
                'edx_django_utils.monitoring.code_owner.utils._PATH_TO_CODE_OWNER_MAPPINGS',
                _process_code_owner_mappings()
        ):
            request = RequestFactory().get('/bad/path/')
            self.middleware(request)
            self._assert_code_owner_custom_metrics(
                mock_set_custom_metric, has_path_error=True, has_transaction_error=True
            )

    @patch('edx_django_utils.monitoring.code_owner.middleware.set_custom_metric')
    def test_code_owner_no_mappings(self, mock_set_custom_metric):
        request = RequestFactory().get('/test/')
        self.middleware(request)
        mock_set_custom_metric.assert_not_called()

    @override_settings(
        CODE_OWNER_MAPPINGS={'team-red': ['lms.djangoapps.monitoring.tests.mock_views']},
    )
    @patch('edx_django_utils.monitoring.code_owner.middleware.set_custom_metric')
    def test_no_resolver_for_path_and_no_transaction(self, mock_set_custom_metric):
        with patch(
                'edx_django_utils.monitoring.code_owner.utils._PATH_TO_CODE_OWNER_MAPPINGS',
                _process_code_owner_mappings()
        ):
            request = RequestFactory().get('/bad/path/')
            self.middleware(request)
            self._assert_code_owner_custom_metrics(
                mock_set_custom_metric, has_path_error=True, has_transaction_error=True
            )

    @override_settings(
        CODE_OWNER_MAPPINGS=['invalid_setting_as_list'],
        ROOT_URLCONF=__name__,
    )
    @patch('edx_django_utils.monitoring.code_owner.middleware.set_custom_metric')
    def test_load_config_with_invalid_dict(self, mock_set_custom_metric):
        with patch(
                'edx_django_utils.monitoring.code_owner.utils._PATH_TO_CODE_OWNER_MAPPINGS',
                _process_code_owner_mappings()
        ):
            request = RequestFactory().get('/test/')
            self.middleware(request)
            expected_path_module = self._REQUEST_PATH_TO_MODULE_PATH['/test/']
            self._assert_code_owner_custom_metrics(
                mock_set_custom_metric, path_module=expected_path_module,
                has_path_error=True, has_transaction_error=True
            )

    def _assert_code_owner_custom_metrics(self, mock_set_custom_metric, expected_code_owner=None,
                                          path_module=None, has_path_error=False,
                                          transaction_name=None, has_transaction_error=False):
        """ Performs a set of assertions around having set the proper custom metrics. """
        call_list = []
        if expected_code_owner:
            call_list.append(call('code_owner', expected_code_owner))
        if path_module:
            call_list.append(call('code_owner_path_module', path_module))
        if has_path_error:
            call_list.append(call('code_owner_path_error', ANY))
        if transaction_name:
            call_list.append(call('code_owner_transaction_name', transaction_name))
        if has_transaction_error:
            call_list.append(call('code_owner_transaction_error', ANY))
        mock_set_custom_metric.assert_has_calls(call_list, any_order=True)
        self.assertEqual(
            len(mock_set_custom_metric.call_args_list), len(call_list),
            'Expected calls {} vs actual calls {}'.format(call_list, mock_set_custom_metric.call_args_list)
        )
