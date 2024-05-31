"""
Tests monitoring middleware.

Note: CachedCustomMonitoringMiddleware is tested in ``test_custom_monitoring.py``.
"""
import re
from unittest.mock import Mock, call, patch

import ddt
from django.core.exceptions import MiddlewareNotUsed
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings
from waffle.testutils import override_switch

from edx_django_utils.cache import RequestCache
from edx_django_utils.monitoring import (
    CookieMonitoringMiddleware,
    DeploymentMonitoringMiddleware,
    FrontendMonitoringMiddleware,
    MonitoringMemoryMiddleware
)


class TestMonitoringMemoryMiddleware(TestCase):
    """
    Tests for MonitoringMemoryMiddleware
    """
    @override_switch('edx_django_utils.monitoring.enable_memory_middleware', False)
    @patch('edx_django_utils.monitoring.internal.middleware.log')
    def test_memory_monitoring_when_disabled(self, mock_logger):
        mock_response = Mock()
        MonitoringMemoryMiddleware(mock_response).process_response(
            'fake request',
            'fake response',
        )
        mock_logger.info.assert_not_called()

    @override_switch('edx_django_utils.monitoring.enable_memory_middleware', True)
    @patch('edx_django_utils.monitoring.internal.middleware.log')
    def test_memory_monitoring_when_enabled(self, mock_logger):
        request = RequestFactory().get('/')
        mock_response = Mock()
        MonitoringMemoryMiddleware(mock_response).process_response(
            request,
            'fake response',
        )
        mock_logger.info.assert_called()


class TestDeploymentMonitoringMiddleware(TestCase):
    """
    Test the DeploymentMonitoringMiddleware functionalities
    """
    version_pattern = r'\d+(\.\d+){2}'

    def setUp(self):
        super().setUp()
        RequestCache.clear_all_namespaces()

    def _test_key_value_pair(self, function_call, key):
        """
        Asserts the function call key and value with the provided key and the default version_pattern
        """
        attribute_key, attribute_value = function_call[0]
        assert attribute_key == key
        assert re.match(re.compile(self.version_pattern), attribute_value)

    @patch('newrelic.agent')
    def test_record_python_and_django_version(self, mock_newrelic_agent):
        """
        Test that the DeploymentMonitoringMiddleware records the correct Python and Django versions
        """
        middleware = DeploymentMonitoringMiddleware(Mock())
        middleware(Mock())

        parameter_calls_count = mock_newrelic_agent.add_custom_parameter.call_count
        assert parameter_calls_count == 2

        function_calls = mock_newrelic_agent.add_custom_parameter.call_args_list
        self._test_key_value_pair(function_calls[0], 'python_version')
        self._test_key_value_pair(function_calls[1], 'django_version')


@ddt.ddt
class CookieMonitoringMiddlewareTestCase(TestCase):
    """
    Tests for CookieMonitoringMiddleware.
    """
    def setUp(self):
        super().setUp()
        self.mock_response = Mock()

    @patch('edx_django_utils.monitoring.internal.middleware.log', autospec=True)
    @patch("edx_django_utils.monitoring.internal.middleware._set_custom_attribute")
    @ddt.data(
        (None, None),  # logging threshold not defined
        (5, None),  # logging threshold too high
        (5, 9999999999999999999),  # logging threshold too high, and random sampling impossibly unlikely
    )
    @ddt.unpack
    def test_cookie_monitoring_with_no_logging(
        self, logging_threshold, sampling_request_count, mock_set_custom_attribute, mock_logger
    ):
        expected_response = self.mock_response
        middleware = CookieMonitoringMiddleware(lambda request: expected_response)
        cookies_dict = {'a': 'y'}

        with override_settings(COOKIE_HEADER_SIZE_LOGGING_THRESHOLD=logging_threshold):
            with override_settings(COOKIE_SAMPLING_REQUEST_COUNT=sampling_request_count):
                actual_response = middleware(self.get_mock_request(cookies_dict))

        assert actual_response == expected_response
        # expect monitoring of header size for all requests
        mock_set_custom_attribute.assert_called_once_with('cookies.header.size', 3)
        # cookie logging was not enabled, so nothing should be logged
        mock_logger.info.assert_not_called()
        mock_logger.exception.assert_not_called()

    @override_settings(COOKIE_HEADER_SIZE_LOGGING_THRESHOLD=None)
    @override_settings(COOKIE_SAMPLING_REQUEST_COUNT=None)
    @patch("edx_django_utils.monitoring.internal.middleware._set_custom_attribute")
    @ddt.data(
        # A corrupt cookie header contains "Cookie: ".
        ('corruptCookie: normal-cookie=value', 1, 1),
        ('corrupt1Cookie: normal-cookie1=value1;corrupt2Cookie: normal-cookie2=value2', 2, 2),
        ('corrupt=Cookie: value', 1, 0),
    )
    @ddt.unpack
    def test_cookie_header_corrupt_monitoring(
        self, corrupt_cookie_header, expected_corrupt_count, expected_corrupt_key_count, mock_set_custom_attribute
    ):
        middleware = CookieMonitoringMiddleware(self.mock_response)
        request = RequestFactory().request()
        request.META['HTTP_COOKIE'] = corrupt_cookie_header

        middleware(request)

        mock_set_custom_attribute.assert_has_calls([
            call('cookies.header.size', len(request.META['HTTP_COOKIE'])),
            call('cookies.header.corrupt_count', expected_corrupt_count),
            call('cookies.header.corrupt_key_count', expected_corrupt_key_count),
        ])

    @override_settings(COOKIE_HEADER_SIZE_LOGGING_THRESHOLD=1)
    @patch('edx_django_utils.monitoring.internal.middleware.log', autospec=True)
    @patch("edx_django_utils.monitoring.internal.middleware._set_custom_attribute")
    def test_log_cookie_with_threshold_met(self, mock_set_custom_attribute, mock_logger):
        middleware = CookieMonitoringMiddleware(self.mock_response)
        cookies_dict = {
            "a": "yy",
            "b": "xxx",
            "c": "z",
        }

        middleware(self.get_mock_request(cookies_dict))

        mock_set_custom_attribute.assert_has_calls([
            call('cookies.header.size', 16),
            call('cookies.header.size.computed', 16)
        ])
        mock_logger.info.assert_called_once_with(
            "Large (>= 1) cookie header detected. BEGIN-COOKIE-SIZES(total=16) b: 3, a: 2, c: 1 END-COOKIE-SIZES"
        )
        mock_logger.exception.assert_not_called()

    @override_settings(
        COOKIE_HEADER_SIZE_LOGGING_THRESHOLD=1,
        UNUSUAL_COOKIE_HEADER_PUBLIC_KEY="some private key",
    )
    @patch('edx_django_utils.monitoring.internal.middleware.log', autospec=True)
    @patch("edx_django_utils.monitoring.internal.middleware.encrypt_for_log", return_value="[encrypted: 50M3JUN|<]")
    def test_log_corrupt_cookies(self, mock_encrypt, mock_logger):
        middleware = CookieMonitoringMiddleware(self.mock_response)
        request = RequestFactory().request()
        request.META['HTTP_COOKIE'] = 'aa=1; bCookie: bb=22; ccc=3Cookie: 33'
        request.META['HTTP_SOMETHING'] = 'else'

        middleware(request)

        # Is passed all headers
        mock_encrypt.assert_called_once_with(
            '{"Cookie": "aa=1; bCookie: bb=22; ccc=3Cookie: 33", "Something": "else"}',
            "some private key",
        )

        # Encrypted headers are logged in additional message if any cookies appeared corrupted.
        mock_logger.info.assert_has_calls([
            call("All headers for request with corrupted cookies (count=2): [encrypted: 50M3JUN|<]"),
            call(
                "Large (>= 1) cookie header detected. "
                "BEGIN-COOKIE-SIZES(total=37) ccc: 11, bCookie: bb: 2, aa: 1 END-COOKIE-SIZES"
            ),
        ])

    @override_settings(
        COOKIE_HEADER_SIZE_LOGGING_THRESHOLD=1,
        UNUSUAL_COOKIE_HEADER_PUBLIC_KEY="some private key",
        UNUSUAL_COOKIE_HEADER_LOG_CHUNK=75,
    )
    @patch('edx_django_utils.monitoring.internal.middleware.log', autospec=True)
    @patch(
        "edx_django_utils.monitoring.internal.middleware.encrypt_for_log",
        return_value="[encrypted: 50M3JUN|<_aaaabbbbccccdddd]"
    )
    def test_log_corrupt_cookies_split(self, mock_encrypt, mock_logger):
        """
        Like ``test_log_corrupt_cookies`` but with message splitting.
        """
        middleware = CookieMonitoringMiddleware(self.mock_response)
        request = RequestFactory().request()
        request.META['HTTP_COOKIE'] = 'aa=1; bCookie: bb=22; ccc=3Cookie: 33'
        request.META['HTTP_SOMETHING'] = 'else'

        middleware(request)

        # Is passed all headers
        mock_encrypt.assert_called_once_with(
            '{"Cookie": "aa=1; bCookie: bb=22; ccc=3Cookie: 33", "Something": "else"}',
            "some private key",
        )

        # Encrypted headers are logged across multiple messages if too large.
        mock_logger.info.assert_has_calls([
            call(
                "All headers for request with corrupted cookies (count=2): "
                "[encrypted: 50M3J [chunk #1, group=OUMTkx5O continues]"
            ),
            call("UN|<_aaaabbbbccccdddd] [chunk #2, group=OUMTkx5O final]"),
            call(
                "Large (>= 1) cookie header detected. "
                "BEGIN-COOKIE-SIZES(total=37) ccc: 11, bCookie: bb: 2, aa: 1 END-COOKIE-SIZES"
            ),
        ])

    @override_settings(COOKIE_HEADER_SIZE_LOGGING_THRESHOLD=9999)
    @override_settings(COOKIE_SAMPLING_REQUEST_COUNT=1)
    @patch('edx_django_utils.monitoring.internal.middleware.log', autospec=True)
    @patch("edx_django_utils.monitoring.internal.middleware._set_custom_attribute")
    def test_log_cookie_with_sampling(self, mock_set_custom_attribute, mock_logger):
        middleware = CookieMonitoringMiddleware(self.mock_response)
        cookies_dict = {
            "a": "yy",
            "b": "xxx",
            "c": "z",
        }

        middleware(self.get_mock_request(cookies_dict))

        mock_set_custom_attribute.assert_has_calls([
            call('cookies.header.size', 16),
            call('cookies.header.size.computed', 16)
        ])
        mock_logger.info.assert_called_once_with(
            "Sampled small (< 9999) cookie header. BEGIN-COOKIE-SIZES(total=16) b: 3, a: 2, c: 1 END-COOKIE-SIZES"
        )
        mock_logger.exception.assert_not_called()

    @override_settings(COOKIE_HEADER_SIZE_LOGGING_THRESHOLD=9999)
    @override_settings(COOKIE_SAMPLING_REQUEST_COUNT=1)
    @patch('edx_django_utils.monitoring.internal.middleware.log', autospec=True)
    @patch("edx_django_utils.monitoring.internal.middleware._set_custom_attribute")
    def test_empty_cookie_header_skips_sampling(self, mock_set_custom_attribute, mock_logger):
        middleware = CookieMonitoringMiddleware(self.mock_response)
        cookies_dict = {}

        middleware(self.get_mock_request(cookies_dict))

        mock_set_custom_attribute.assert_has_calls([
            call('cookies.header.size', 0),
        ])
        mock_logger.info.assert_not_called()
        mock_logger.exception.assert_not_called()

    @patch('edx_django_utils.monitoring.internal.middleware.log', autospec=True)
    def test_cookie_monitoring_unknown_exception(self, mock_logger):
        middleware = CookieMonitoringMiddleware(self.mock_response)
        cookies_dict = {'a': 'y'}
        mock_request = self.get_mock_request(cookies_dict)
        mock_request.META = Mock()
        mock_request.META.side_effect = Exception("Some exception")

        middleware(mock_request)

        mock_logger.exception.assert_called_once_with("Unexpected error logging and monitoring cookies.")

    @override_settings(COOKIE_PREFIXES_TO_REMOVE=[('old_cookie', 'localhost')])
    def test_deprecated_cookies_removed(self):
        self.mock_response.reset_mock()
        middleware = CookieMonitoringMiddleware(lambda _: self.mock_response)
        cookies_dict = {'old_cookie': 'x',
                        'ok_cookie': 'x',
                        'old_cookie_9000': 'x'
                        }
        response = middleware(self.get_mock_request(cookies_dict))

        assert response == self.mock_response
        assert response.delete_cookie.mock_calls == [
            call('old_cookie',  domain='localhost'),
            call('old_cookie_9000', domain='localhost'),
        ]

    @override_settings(COOKIE_PREFIXES_TO_REMOVE='old_cookie')
    @patch('edx_django_utils.monitoring.internal.middleware.log', autospec=True)
    def test_bad_cookie_prefix_setting(self, mock_log):
        self.mock_response.reset_mock()
        middleware = CookieMonitoringMiddleware(lambda _: self.mock_response)
        cookies_dict = {'old_cookie': 'x',
                        'ok_cookie': 'x',
                        'old_cookie_9000': 'x'
                        }
        response = middleware(self.get_mock_request(cookies_dict))

        assert response == self.mock_response
        mock_log.warning.assert_called_once_with("COOKIE_PREFIXES_TO_REMOVE must be a list of (name, domain) tuples,"
                                                 " not <class 'str'>. No cookies will be removed.")
        response.delete_cookie.assert_not_called()

    def get_mock_request(self, cookies_dict):
        """
        Return mock request with the provided cookies in the header.
        """
        factory = RequestFactory()
        for name, value in cookies_dict.items():
            factory.cookies[name] = value
        return factory.request()


@ddt.ddt
class FrontendMonitoringMiddlewareTestCase(TestCase):
    """
    Tests for FrontendMonitoringMiddleware.
    """
    def setUp(self):
        super().setUp()
        self.script = "<script>test script</script>"

    @override_switch('edx_django_utils.monitoring.enable_frontend_monitoring_middleware', False)
    def test_frontend_middleware_with_waffle_diasbled(self):
        """
        Test that middleware is disabled when waffle flag is not enabled.
        """
        original_html = '<head></head>'
        with override_settings(OPENEDX_TELEMETRY_FRONTEND_SCRIPTS=self.script):
            self.assertRaises(
                MiddlewareNotUsed,
                FrontendMonitoringMiddleware,
                lambda r: HttpResponse(original_html, content_type='text/html')
            )

    @override_switch('edx_django_utils.monitoring.enable_frontend_monitoring_middleware', True)
    def test_frontend_middleware_with_waffle_enabled(self):
        """
        Test that middleware works as expected when flag is enabled.
        """
        with override_settings(OPENEDX_TELEMETRY_FRONTEND_SCRIPTS=self.script):
            middleware = FrontendMonitoringMiddleware(lambda r: HttpResponse('<head></head>', content_type='text/html'))
            response = middleware(HttpRequest())
        # Assert that the script is inserted into the response when flag is enabled
        assert self.script.encode() in response.content

    @override_switch('edx_django_utils.monitoring.enable_frontend_monitoring_middleware', True)
    @patch("edx_django_utils.monitoring.internal.middleware.FrontendMonitoringMiddleware.inject_script")
    def test_frontend_middleware_without_setting_variable(self, mock_inject_script):
        """
        Test that middleware behaves correctly when setting variable is not defined.
        """
        original_html = '<html><head></head><body></body><html>'
        middleware = FrontendMonitoringMiddleware(lambda r: HttpResponse(original_html, content_type='text/html'))
        response = middleware(HttpRequest())
        # Assert that the response content remains unchanged if settings not defined
        assert response.content == original_html.encode()

        mock_inject_script.assert_not_called()

    @override_switch('edx_django_utils.monitoring.enable_frontend_monitoring_middleware', True)
    @patch("edx_django_utils.monitoring.internal.middleware.FrontendMonitoringMiddleware.inject_script")
    def test_frontend_middleware_for_json_requests(self, mock_inject_script):
        """
        Test that middleware doesn't insert script tag for json requests
        """
        middleware = FrontendMonitoringMiddleware(lambda r: JsonResponse({"dummy": True}))
        response = middleware(HttpRequest())
        # Assert that the response content remains unchanged if settings not defined
        assert response.content == b'{"dummy": true}'

        mock_inject_script.assert_not_called()

    @override_switch('edx_django_utils.monitoring.enable_frontend_monitoring_middleware', True)
    @ddt.data(
        ('<html><body></body><html>', '<body>'),
        ('<html><head></head><body></body><html>', '</head>'),
        ('<head></head><body></body>', '</head>'),
        ('<body></body>', '<body>'),
        ('<head></head>', '</head>'),
    )
    @ddt.unpack
    def test_frontend_middleware_with_head_and_body_tag(self, original_html, expected_tag):
        """
        Test that script is inserted at the right place.
        """
        with override_settings(OPENEDX_TELEMETRY_FRONTEND_SCRIPTS=self.script):
            middleware = FrontendMonitoringMiddleware(lambda r: HttpResponse(original_html, content_type='text/html'))
            response = middleware(HttpRequest())

        # Assert that the script is inserted at the right place
        assert f"{self.script}{expected_tag}".encode() in response.content

    @override_switch('edx_django_utils.monitoring.enable_frontend_monitoring_middleware', True)
    @ddt.data(
        '<html></html>',
        '<center></center>',
    )
    def test_frontend_middleware_without_head_and_body_tag(self, original_html):
        """
        Test that middleware behavior is correct when both of head and body tag are missing in the response.
        """
        with override_settings(OPENEDX_TELEMETRY_FRONTEND_SCRIPTS=self.script):
            middleware = FrontendMonitoringMiddleware(lambda r: HttpResponse(original_html, content_type='text/html'))
            response = middleware(HttpRequest())
        # Assert that the response content remains unchanged if no body tag is found
        assert response.content == original_html.encode()

    @override_switch('edx_django_utils.monitoring.enable_frontend_monitoring_middleware', True)
    def test_frontend_middleware_content_length_header_already_set(self):
        """
        Test that middleware updates the Content-Length header, when its already set.
        """
        original_html = '<head></head>'
        with override_settings(OPENEDX_TELEMETRY_FRONTEND_SCRIPTS=self.script):
            middleware = FrontendMonitoringMiddleware(lambda r: HttpResponse(
                original_html, content_type='text/html', headers={'Content-Length': len(original_html)}))
            response = middleware(HttpRequest())
        # Assert that the response content contains script tag
        assert self.script.encode() in response.content
        # Assert that the Content-Length header is updated and script length is added.
        assert response.headers.get('Content-Length') == str(len(original_html) + len(self.script))

    @override_switch('edx_django_utils.monitoring.enable_frontend_monitoring_middleware', True)
    def test_frontend_middleware_content_length_header_not_set(self):
        """
        Test that middleware doesn't set the Content-Length header when it's not already set.
        """
        original_html = '<head></head>'
        with override_settings(OPENEDX_TELEMETRY_FRONTEND_SCRIPTS=self.script):
            middleware = FrontendMonitoringMiddleware(lambda r: HttpResponse(original_html, content_type='text/html'))
            response = middleware(HttpRequest())
        # Assert that the response content contains script tag
        assert self.script.encode() in response.content
        # Assert that the Content-Length header isn't updated, when not set already
        assert response.headers.get('Content-Length') is None
