"""
Tests for the private utils.
"""
import unittest

import django
from django.test import TestCase, override_settings

from edx_django_utils.private_utils import _check_middleware_dependencies


class _TestMiddleware:
    pass


class TestPrivateUtils(TestCase):  # pylint: disable=missing-class-docstring

    @override_settings(MIDDLEWARE=['required.Middleware'])
    def test_check_middleware_dependencies_simple_success(self):
        middleware = _TestMiddleware()
        _check_middleware_dependencies(middleware, required_middleware=['required.Middleware'])

    @unittest.skipIf(django.VERSION[0] > 1, 'MIDDLEWARE_CLASSES only works with less than django-2 versions.')
    @override_settings(MIDDLEWARE_CLASSES=['required.Middleware'])
    def test_check_middleware_dependencies_simple__classes_success(self):
        middleware = _TestMiddleware()
        _check_middleware_dependencies(middleware, required_middleware=['required.Middleware'])

    @override_settings(MIDDLEWARE=[
        'some.1.Middleware',
        'required.2.Middleware',
        'some.3.Middleware',
        'required.4.Middleware',
    ])
    def test_check_middleware_dependencies_complex_success(self):
        middleware = _TestMiddleware()
        _check_middleware_dependencies(middleware, required_middleware=[
            'required.2.Middleware',
            'required.4.Middleware',
        ])

    @override_settings(MIDDLEWARE=['some.Middleware'])
    def test_check_middleware_dependencies_missing(self):
        middleware = _TestMiddleware()
        with self.assertRaises(AssertionError):
            _check_middleware_dependencies(middleware, required_middleware=['missing.Middleware'])

    @override_settings(MIDDLEWARE_CLASSES=['some.Middleware'])
    def test_check_middleware_dependencies_missing_classes(self):
        middleware = _TestMiddleware()
        with self.assertRaises(AssertionError):
            _check_middleware_dependencies(middleware, required_middleware=['missing.Middleware'])

    @override_settings(MIDDLEWARE=['required.2.Middleware', 'required.1.Middleware'])
    def test_check_middleware_dependencies_bad_order(self):
        middleware = _TestMiddleware()
        with self.assertRaises(AssertionError):
            _check_middleware_dependencies(middleware, required_middleware=[
                'required.1.Middleware',
                'required.2.Middleware',
            ])
