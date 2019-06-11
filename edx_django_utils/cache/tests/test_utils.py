# -*- coding: utf-8 -*-
"""
Tests for the request cache.
"""
# pylint: disable=missing-docstring

from threading import Thread
from unittest import TestCase

import mock

from edx_django_utils.cache.utils import (
    DEFAULT_REQUEST_CACHE_NAMESPACE,
    SHOULD_FORCE_CACHE_MISS_KEY,
    CachedResponse,
    CachedResponseError,
    RequestCache,
    TieredCache
)

TEST_KEY = u"clöbert"
TEST_KEY_2 = u"clöbert2"
TEST_KEY_UNICODE = u"clöbert"
EXPECTED_VALUE = u"bertclöb"
EXPECTED_VALUE_2 = u"bertclöb2"
TEST_NAMESPACE = u"test_namespåce"
TEST_DJANGO_TIMEOUT_CACHE = 1


class TestRequestCache(TestCase):
    def setUp(self):
        super(TestRequestCache, self).setUp()
        RequestCache.clear_all_namespaces()
        self.request_cache = RequestCache()
        self.other_request_cache = RequestCache(TEST_NAMESPACE)

    def test_get_cached_response_hit(self):
        self.request_cache.set(TEST_KEY, EXPECTED_VALUE)
        cached_response = self.request_cache.get_cached_response(TEST_KEY)
        self.assertTrue(cached_response.is_found)
        self.assertEqual(cached_response.value, EXPECTED_VALUE)
        cached_response = self.other_request_cache.get_cached_response(TEST_KEY)
        self.assertFalse(cached_response.is_found)

        self.other_request_cache.set(TEST_KEY_2, EXPECTED_VALUE)
        cached_response = self.request_cache.get_cached_response(TEST_KEY_2)
        self.assertFalse(cached_response.is_found)
        cached_response = self.other_request_cache.get_cached_response(TEST_KEY_2)
        self.assertTrue(cached_response.is_found)
        self.assertEqual(cached_response.value, EXPECTED_VALUE)

    def test_get_cached_response_hit_with_cached_none(self):
        self.request_cache.set(TEST_KEY, None)
        cached_response = self.request_cache.get_cached_response(TEST_KEY)
        self.assertTrue(cached_response.is_found)
        self.assertEqual(cached_response.value, None)

    def test_get_cached_response_miss(self):
        cached_response = self.request_cache.get_cached_response(TEST_KEY)
        self.assertFalse(cached_response.is_found)

    def test_get_cached_response_with_default(self):
        self.request_cache.setdefault(TEST_KEY, EXPECTED_VALUE)
        cached_response = self.request_cache.get_cached_response(TEST_KEY)
        self.assertTrue(cached_response.is_found)
        self.assertEqual(cached_response.value, EXPECTED_VALUE)

    def test_get_cached_response_with_default_after_set(self):
        self.request_cache.set(TEST_KEY, EXPECTED_VALUE_2)
        self.request_cache.setdefault(TEST_KEY, EXPECTED_VALUE)
        cached_response = self.request_cache.get_cached_response(TEST_KEY)
        self.assertTrue(cached_response.is_found)
        self.assertEqual(cached_response.value, EXPECTED_VALUE_2)

    def test_cache_data(self):
        self.assertDictEqual(self.request_cache.data, {})

        key_value_pairs = [
            (TEST_KEY, EXPECTED_VALUE),
            (TEST_KEY_2, EXPECTED_VALUE_2)
        ]
        expected_dict = {}
        for key, value in key_value_pairs:
            self.request_cache.set(key, value)
            expected_dict[key] = value

        self.assertDictEqual(self.request_cache.data, expected_dict)

    def test_clear(self):
        self.request_cache.set(TEST_KEY, EXPECTED_VALUE)
        self.other_request_cache.set(TEST_KEY, EXPECTED_VALUE)
        self.request_cache.clear()
        cached_response = self.request_cache.get_cached_response(TEST_KEY)
        self.assertFalse(cached_response.is_found)
        cached_response = self.other_request_cache.get_cached_response(TEST_KEY)
        self.assertTrue(cached_response.is_found)

    def test_clear_all_namespaces(self):
        self.request_cache.set(TEST_KEY, EXPECTED_VALUE)
        self.other_request_cache.set(TEST_KEY, EXPECTED_VALUE)
        RequestCache.clear_all_namespaces()
        cached_response = self.request_cache.get_cached_response(TEST_KEY)
        self.assertFalse(cached_response.is_found)

        cached_response = self.other_request_cache.get_cached_response(TEST_KEY)
        self.assertFalse(cached_response.is_found)

    def test_clear_all_namespaces_other_thread(self):
        """
        Clearing all namespaces for a different thread should not clear this
        request cache.
        """
        self.request_cache.set(TEST_KEY, EXPECTED_VALUE)
        other_thread = Thread(target=lambda: RequestCache.clear_all_namespaces())  # pylint: disable=unnecessary-lambda
        other_thread.start()
        other_thread.join()

        cached_response = self.request_cache.get_cached_response(TEST_KEY)
        self.assertTrue(cached_response.is_found)

    def test_delete(self):
        self.request_cache.set(TEST_KEY, EXPECTED_VALUE)
        self.request_cache.set(TEST_KEY_2, EXPECTED_VALUE)
        self.other_request_cache.set(TEST_KEY, EXPECTED_VALUE)
        self.request_cache.delete(TEST_KEY)

        cached_response = self.request_cache.get_cached_response(TEST_KEY)
        self.assertFalse(cached_response.is_found)
        cached_response = self.request_cache.get_cached_response(TEST_KEY_2)
        self.assertTrue(cached_response.is_found)
        self.assertEqual(cached_response.value, EXPECTED_VALUE)
        cached_response = self.other_request_cache.get_cached_response(TEST_KEY)
        self.assertTrue(cached_response.is_found)

    def test_delete_missing_key(self):
        try:
            self.request_cache.delete(TEST_KEY)
        except KeyError:
            self.fail('Deleting a missing key from the request cache should not cause an error.')

    def test_create_request_cache_with_default_namespace(self):
        with self.assertRaises(AssertionError):
            RequestCache(DEFAULT_REQUEST_CACHE_NAMESPACE)


class TestTieredCache(TestCase):
    def setUp(self):
        super(TestTieredCache, self).setUp()
        self.request_cache = RequestCache()
        TieredCache.dangerous_clear_all_tiers()

    def test_get_cached_response_all_tier_miss(self):
        cached_response = TieredCache.get_cached_response(TEST_KEY)
        self.assertFalse(cached_response.is_found)

    def test_get_cached_response_request_cache_hit(self):
        self.request_cache.set(TEST_KEY, EXPECTED_VALUE)
        cached_response = TieredCache.get_cached_response(TEST_KEY)
        self.assertTrue(cached_response.is_found)
        self.assertEqual(cached_response.value, EXPECTED_VALUE)

    @mock.patch('django.core.cache.cache.get')
    def test_get_cached_response_django_cache_hit(self, mock_cache_get):
        mock_cache_get.return_value = EXPECTED_VALUE
        cached_response = TieredCache.get_cached_response(TEST_KEY)
        self.assertTrue(cached_response.is_found)
        self.assertEqual(cached_response.value, EXPECTED_VALUE)

        cached_response = self.request_cache.get_cached_response(TEST_KEY)
        self.assertTrue(cached_response.is_found, 'Django cache hit should cache value in request cache.')

    @mock.patch('django.core.cache.cache.get')
    def test_get_cached_response_force_cache_miss(self, mock_cache_get):
        self.request_cache.set(SHOULD_FORCE_CACHE_MISS_KEY, True)
        mock_cache_get.return_value = EXPECTED_VALUE
        cached_response = TieredCache.get_cached_response(TEST_KEY)
        self.assertFalse(cached_response.is_found)

        cached_response = self.request_cache.get_cached_response(TEST_KEY)
        self.assertFalse(cached_response.is_found, 'Forced Django cache miss should not cache value in request cache.')

    @mock.patch('django.core.cache.cache.set')
    def test_set_all_tiers(self, mock_cache_set):
        mock_cache_set.return_value = EXPECTED_VALUE
        TieredCache.set_all_tiers(TEST_KEY, EXPECTED_VALUE, TEST_DJANGO_TIMEOUT_CACHE)
        mock_cache_set.assert_called_with(TEST_KEY, EXPECTED_VALUE, TEST_DJANGO_TIMEOUT_CACHE)
        self.assertEqual(self.request_cache.get_cached_response(TEST_KEY).value, EXPECTED_VALUE)

    @mock.patch('django.core.cache.cache.clear')
    def test_dangerous_clear_all_tiers_and_namespaces(self, mock_cache_clear):
        TieredCache.set_all_tiers(TEST_KEY, EXPECTED_VALUE)
        TieredCache.dangerous_clear_all_tiers()
        self.assertFalse(self.request_cache.get_cached_response(TEST_KEY).is_found)
        mock_cache_clear.assert_called_once_with()

    @mock.patch('django.core.cache.cache.delete')
    def test_delete(self, mock_cache_delete):
        TieredCache.set_all_tiers(TEST_KEY, EXPECTED_VALUE)
        TieredCache.set_all_tiers(TEST_KEY_2, EXPECTED_VALUE)
        TieredCache.delete_all_tiers(TEST_KEY)
        self.assertFalse(self.request_cache.get_cached_response(TEST_KEY).is_found)
        self.assertEqual(self.request_cache.get_cached_response(TEST_KEY_2).value, EXPECTED_VALUE)
        mock_cache_delete.assert_called_with(TEST_KEY)


class CacheResponseTests(TestCase):
    def test_is_miss(self):
        is_found = False
        cached_response = CachedResponse(is_found, TEST_KEY, EXPECTED_VALUE)
        self.assertFalse(cached_response.is_found)
        self.assertEqual(cached_response.key, TEST_KEY)
        with self.assertRaises(AttributeError):
            cached_response.value  # pylint: disable=pointless-statement
        self.assertEqual(cached_response.get_value_or_default(EXPECTED_VALUE_2), EXPECTED_VALUE_2)
        self.assertIn(u'CachedResponse(is_found={}, key={}'.format(False, TEST_KEY), cached_response.__repr__())

    def test_is_hit(self):
        is_found = True
        cached_response = CachedResponse(is_found, TEST_KEY, EXPECTED_VALUE)
        self.assertTrue(cached_response.is_found)
        self.assertEqual(cached_response.key, TEST_KEY)
        self.assertEqual(cached_response.value, EXPECTED_VALUE)
        self.assertEqual(cached_response.get_value_or_default(EXPECTED_VALUE_2), EXPECTED_VALUE)
        self.assertIn(u'CachedResponse(is_found={}, key={}'.format(True, TEST_KEY), cached_response.__repr__())

    def test_cached_response_equals(self):
        self.assertEqual(
            CachedResponse(True, TEST_KEY, EXPECTED_VALUE),
            CachedResponse(True, TEST_KEY, EXPECTED_VALUE),
        )
        self.assertEqual(
            CachedResponse(False, TEST_KEY, EXPECTED_VALUE),
            CachedResponse(False, TEST_KEY, EXPECTED_VALUE),
        )

        self.assertNotEqual(
            CachedResponse(True, TEST_KEY, EXPECTED_VALUE),
            CachedResponse(False, TEST_KEY, EXPECTED_VALUE),
        )
        self.assertNotEqual(
            CachedResponse(True, TEST_KEY, EXPECTED_VALUE),
            CachedResponse(True, TEST_KEY_2, EXPECTED_VALUE),
        )
        self.assertNotEqual(
            CachedResponse(True, TEST_KEY, EXPECTED_VALUE),
            CachedResponse(True, TEST_KEY, EXPECTED_VALUE_2),
        )

    def test_cached_response_not_equals(self):
        self.assertNotEqual(
            CachedResponse(True, TEST_KEY, EXPECTED_VALUE), CachedResponse(True, TEST_KEY, EXPECTED_VALUE_2)
        )

    def test_cached_response_misuse(self):
        cached_response = CachedResponse(True, TEST_KEY, EXPECTED_VALUE)

        with self.assertRaises(CachedResponseError):
            bool(cached_response)

        with self.assertRaises(CachedResponseError):
            # For Python 3
            cached_response.__bool__()

        with self.assertRaises(CachedResponseError):
            other_object = object()
            cached_response == other_object  # pylint: disable=pointless-statement
