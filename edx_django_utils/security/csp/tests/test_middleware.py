"""
Tests for Content-Security-Policy middleware.
"""

import warnings
from unittest import TestCase
from unittest.mock import Mock, patch

import ddt
import pytest
from django.core.exceptions import MiddlewareNotUsed
from django.test import override_settings

import edx_arch_experiments.csp.middleware as csp


@ddt.ddt
class TestLoadHeaders(TestCase):
    """Test loading of headers from settings."""

    @ddt.unpack
    @ddt.data(
        # Empty settings
        [{}, {}],
        # The reporting URL and endpoint names alone don't do anything
        [{"CSP_REPORTING_URI": "http://localhost"}, {}],
        [{"CSP_REPORTING_NAME": "default"}, {}],
        [
            {
                "CSP_REPORTING_URI": "http://localhost",
                "CSP_REPORTING_NAME": "default"
            },
            {},
        ],
        # Just the enforcement header
        [
            {"CSP_ENFORCE": "default-src https:"},
            {'Content-Security-Policy': "default-src https:"},
        ],
        # Just the reporting header
        [
            {"CSP_REPORT_ONLY": "default-src 'none'"},
            {'Content-Security-Policy-Report-Only': "default-src 'none'"},
        ],
        # Reporting URL is automatically appended to headers
        [
            {
                "CSP_ENFORCE": "default-src https:",
                "CSP_REPORT_ONLY": "default-src 'none'",
                "CSP_REPORTING_URI": "http://localhost",
            },
            {
                'Content-Security-Policy': "default-src https:; report-uri http://localhost",
                'Content-Security-Policy-Report-Only': "default-src 'none'; report-uri http://localhost",
            },
        ],
        # ...and when an endpoint name is supplied,
        # Reporting-Endpoints is added and a report-to directive is
        # included.
        [
            {
                "CSP_ENFORCE": "default-src https:",
                "CSP_REPORT_ONLY": "default-src 'none'",
                "CSP_REPORTING_URI": "http://localhost",
                "CSP_REPORTING_NAME": "default",
            },
            {
                'Reporting-Endpoints': 'default="http://localhost"',
                'Content-Security-Policy': "default-src https:; report-uri http://localhost; report-to default",
                'Content-Security-Policy-Report-Only': (
                    "default-src 'none'; report-uri http://localhost; report-to default"
                ),
            },
        ],
        # Adding a reporting endpoint name without a URL doesn't change anything.
        [
            {
                "CSP_REPORT_ONLY": "default-src 'none'",
                "CSP_REPORTING_NAME": "default",
            },
            {'Content-Security-Policy-Report-Only': "default-src 'none'"},
        ],
        # Any newlines and trailing semicolon are stripped.
        [
            {
                "CSP_REPORT_ONLY": "default-src 'self';   \n \t  frame-src 'none';  \n ",
                "CSP_REPORTING_URI": "http://localhost",
            },
            {
                'Content-Security-Policy-Report-Only': (
                    "default-src 'self'; frame-src 'none'; "
                    "report-uri http://localhost"
                ),
            },
        ],
    )
    def test_load_headers(self, settings, headers):
        with override_settings(**settings):
            assert csp._load_headers() == headers  # pylint: disable=protected-access

    def test_validation(self):
        """When the reporting name is invalid, don't use it."""
        with override_settings(
                CSP_ENFORCE="default-src https:",
                CSP_REPORTING_URI="http://localhost",
                CSP_REPORTING_NAME="&&&&&&&&&&&&",
        ):
            with warnings.catch_warnings(record=True) as warns:
                warnings.simplefilter("always")
                headers = csp._load_headers()  # pylint: disable=protected-access

        assert "CSP_REPORTING_NAME ignored" in warns[0].message.args[0]
        assert headers == {
            'Content-Security-Policy': "default-src https:; report-uri http://localhost"
        }


@ddt.ddt
class TestHeaderManipulation(TestCase):
    """Test _append_headers"""

    @ddt.unpack
    @ddt.data(
        [{}, {}, {}],
        [
            {'existing': 'aaa', 'multi': '111'},
            {'multi': '222', 'new': 'xxx'},
            {'existing': 'aaa', 'multi': '111, 222', 'new': 'xxx'},
        ],
    )
    def test_append_headers(self, response_headers, more_headers, expected):
        csp._append_headers(response_headers, more_headers)  # pylint: disable=protected-access
        assert response_headers == expected


@ddt.ddt
class TestCSPMiddleware(TestCase):
    """Test the actual middleware."""

    def setUp(self):
        super().setUp()
        self.fake_response = Mock()
        self.fake_response.headers = {'Existing': 'something'}

    def test_make_middleware_unused(self):
        with pytest.raises(MiddlewareNotUsed):
            csp.content_security_policy_middleware(lambda _: self.fake_response)

    @ddt.unpack
    @ddt.data(
        [False, {'Existing': 'something'},],
        [
            True, {
                'Existing': 'something',
                'Content-Security-Policy': 'default-src: https:',
            },
        ],
    )
    @override_settings(CSP_ENFORCE="default-src: https:")
    def test_make_middleware_configured(self, flag_enabled, expected_headers):
        handler = csp.content_security_policy_middleware(lambda _: self.fake_response)

        with patch.object(csp, 'FLAG_CSP', autospec=True):
            csp.FLAG_CSP.is_enabled.return_value = flag_enabled
            assert handler(Mock()) is self.fake_response

        # Headers have been mutated in place (if flag enabled)
        assert self.fake_response.headers == expected_headers
