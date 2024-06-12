"""
Tests for Content-Security-Policy middleware.
"""

from unittest import TestCase
from unittest.mock import MagicMock, patch

import ddt
from edx_django_utils.security.clickjacking.middleware import EdxXFrameOptionsMiddleware


@ddt.ddt
class TestEdxXFrameOptionsMiddleware(TestCase):
    """Test the actual middleware."""

    def setUp(self):
        super().setUp()

    @patch('edx_django_utils.security.clickjacking.middleware._validate_header_value')
    @patch('edx_django_utils.security.clickjacking.middleware.settings')
    def test_x_frame_must_be_deny_on_no_override(self, settings, validate_header):
        settings.X_FRAME_OPTIONS = 'DENY'
        validate_header.return_value = True

        request = MagicMock()
        response = MagicMock()
        response.headers = {}
        middleware = EdxXFrameOptionsMiddleware(get_response=lambda _: response)

        middleware.process_response(request, response)

        assert response.headers['X-Frame-Options'] == 'DENY'
        validate_header.assert_called_once_with('DENY')

    @patch('edx_django_utils.security.clickjacking.middleware._validate_header_value')
    @patch('edx_django_utils.security.clickjacking.middleware.settings')
    def test_on_override_with_valid_regex_is_sameorigin(self, settings, validate_header):
        """
        If the URL matches one of the overrides, the header should be set to
        the correct override setting as specified in the `X_FRAME_OPTIONS_OVERRIDES` list.
        """
        settings.X_FRAME_OPTIONS = 'DENY'
        settings.X_FRAME_OPTIONS_OVERRIDES = [['.*/media/scorm/.*', 'SAMEORIGIN']]
        validate_header.return_value = True

        request = MagicMock()
        response = MagicMock()
        response.headers = {}
        request.path = 'http://localhost:18010/media/scorm/hello/world'
        middleware = EdxXFrameOptionsMiddleware(get_response=lambda _: response)

        middleware.process_response(request, response)

        assert response.headers['X-Frame-Options'] == 'SAMEORIGIN'

    @patch('edx_django_utils.security.clickjacking.middleware._validate_header_value')
    @patch('edx_django_utils.security.clickjacking.middleware.settings')
    def test_on_override_for_non_matching_urls_is_deny(self, settings, validate_header):
        """
        If the URL does not match any of the overrides, the header should be set to
        the `X_FRAME_OPTIONS` setting.
        """
        settings.X_FRAME_OPTIONS = 'DENY'
        settings.X_FRAME_OPTIONS_OVERRIDES = [['.*/media/scorm/.*', 'SAMEORIGIN']]
        validate_header.return_value = True

        request = MagicMock()
        response = MagicMock()
        response.headers = {}
        request.path = 'http://localhost:18010/notmedia/scorm/hello/world'
        middleware = EdxXFrameOptionsMiddleware(get_response=lambda _: response)

        middleware.process_response(request, response)

        assert response.headers['X-Frame-Options'] == 'DENY'

    def test_x_frame_defaults_to_deny(self):
        request = MagicMock()
        response = MagicMock()
        response.headers = {}
        middleware = EdxXFrameOptionsMiddleware(get_response=lambda _: response)

        middleware.process_response(request, response)

        assert response.headers['X-Frame-Options'] == 'DENY'
























        # settings.X_FRAME_OPTIONS_OVERRIDES = [['regex', 'SAMEORIGIN']]
        # search.return_value = False
        # middleware.process_response(request, response)
        # assert response.headers['X-Frame-Options'] == 'SAMEORIGIN'
        # validate_header.assert_called_with('SAMEORIGIN')
        # search.assert_called_with('regex')
        # assert response.headers['X-Frame-Options'] == 'SAMEORIGIN'
        # validate_header.assert_called_with('SAMEORIGIN')
        # search.assert_called_with('regex')
        # assert response.headers['X-Frame-Options'] == 'SAMEORIGIN'
