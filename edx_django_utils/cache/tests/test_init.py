"""
Tests for the request cache.
"""
import mock

from edx_django_utils.cache import (
    DEFAULT_REQUEST_CACHE_NAMESPACE,
    SHOULD_FORCE_CACHE_MISS_KEY,
    CachedResponse,
    CachedResponseError,
    RequestCache,
    TieredCache
)
from ecommerce.tests.testcases import TestCase

TEST_KEY = "clobert"
TEST_KEY_2 = "clobert2"
EXPECTED_VALUE = "bertclob"
TEST_NAMESPACE = "test_namespace"
TEST_DJANGO_TIMEOUT_CACHE = 1


class TestRequestCache(TestCase):
    def setUp(self):
        RequestCache.clear_all_namespaces()
        self.request_cache = RequestCache()
        self.other_request_cache = RequestCache(TEST_NAMESPACE)

    def test_get_cached_response_hit(self):
        self.request_cache.set(TEST_KEY, EXPECTED_VALUE)
        cached_response = self.request_cache.get_cached_response(TEST_KEY)
        self.assertTrue(cached_response.is_hit)
        self.assertEqual(cached_response.value, EXPECTED_VALUE)
        cached_response = self.other_request_cache.get_cached_response(TEST_KEY)
        self.assertTrue(cached_response.is_miss)

        self.other_request_cache.set(TEST_KEY_2, EXPECTED_VALUE)
        cached_response = self.request_cache.get_cached_response(TEST_KEY_2)
        self.assertTrue(cached_response.is_miss)
        cached_response = self.other_request_cache.get_cached_response(TEST_KEY_2)
        self.assertTrue(cached_response.is_hit)
        self.assertEqual(cached_response.value, EXPECTED_VALUE)

    def test_get_cached_response_hit_with_cached_none(self):
        self.request_cache.set(TEST_KEY, None)
        cached_response = self.request_cache.get_cached_response(TEST_KEY)
        self.assertFalse(cached_response.is_miss)
        self.assertEqual(cached_response.value, None)

    def test_get_cached_response_miss(self):
        cached_response = self.request_cache.get_cached_response(TEST_KEY)
        self.assertTrue(cached_response.is_miss)

    def test_clear(self):
        self.request_cache.set(TEST_KEY, EXPECTED_VALUE)
        self.other_request_cache.set(TEST_KEY, EXPECTED_VALUE)
        self.request_cache.clear()
        cached_response = self.request_cache.get_cached_response(TEST_KEY)
        self.assertTrue(cached_response.is_miss)
        cached_response = self.other_request_cache.get_cached_response(TEST_KEY)
        self.assertTrue(cached_response.is_hit)

    def test_clear_all_namespaces(self):
        self.request_cache.set(TEST_KEY, EXPECTED_VALUE)
        self.other_request_cache.set(TEST_KEY, EXPECTED_VALUE)
        RequestCache.clear_all_namespaces()
        cached_response = self.request_cache.get_cached_response(TEST_KEY)
        self.assertTrue(cached_response.is_miss)

        cached_response = self.other_request_cache.get_cached_response(TEST_KEY)
        self.assertTrue(cached_response.is_miss)

    def test_delete(self):
        self.request_cache.set(TEST_KEY, EXPECTED_VALUE)
        self.request_cache.set(TEST_KEY_2, EXPECTED_VALUE)
        self.other_request_cache.set(TEST_KEY, EXPECTED_VALUE)
        self.request_cache.delete(TEST_KEY)

        cached_response = self.request_cache.get_cached_response(TEST_KEY)
        self.assertTrue(cached_response.is_miss)
        cached_response = self.request_cache.get_cached_response(TEST_KEY_2)
        self.assertTrue(cached_response.is_hit)
        self.assertEqual(cached_response.value, EXPECTED_VALUE)
        cached_response = self.other_request_cache.get_cached_response(TEST_KEY)
        self.assertTrue(cached_response.is_hit)

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
        self.request_cache = RequestCache()
        TieredCache.dangerous_clear_all_tiers()

    def test_get_cached_response_all_tier_miss(self):
        cached_response = TieredCache.get_cached_response(TEST_KEY)
        self.assertTrue(cached_response.is_miss)

    def test_get_cached_response_request_cache_hit(self):
        self.request_cache.set(TEST_KEY, EXPECTED_VALUE)
        cached_response = TieredCache.get_cached_response(TEST_KEY)
        self.assertTrue(cached_response.is_hit)
        self.assertEqual(cached_response.value, EXPECTED_VALUE)

    @mock.patch('django.core.cache.cache.get')
    def test_get_cached_response_django_cache_hit(self, mock_cache_get):
        mock_cache_get.return_value = EXPECTED_VALUE
        cached_response = TieredCache.get_cached_response(TEST_KEY)
        self.assertTrue(cached_response.is_hit)
        self.assertEqual(cached_response.value, EXPECTED_VALUE)

        cached_response = self.request_cache.get_cached_response(TEST_KEY)
        self.assertTrue(cached_response.is_hit, 'Django cache hit should cache value in request cache.')

    @mock.patch('django.core.cache.cache.get')
    def test_get_cached_response_force_django_cache_miss(self, mock_cache_get):
        self.request_cache.set(SHOULD_FORCE_CACHE_MISS_KEY, True)
        mock_cache_get.return_value = EXPECTED_VALUE
        cached_response = TieredCache.get_cached_response(TEST_KEY)
        self.assertTrue(cached_response.is_miss)

        cached_response = self.request_cache.get_cached_response(TEST_KEY)
        self.assertTrue(cached_response.is_miss, 'Forced Django cache miss should not cache value in request cache.')

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
        self.assertTrue(self.request_cache.get_cached_response(TEST_KEY).is_miss)
        mock_cache_clear.assert_called_once_with()

    @mock.patch('django.core.cache.cache.delete')
    def test_delete(self, mock_cache_delete):
        TieredCache.set_all_tiers(TEST_KEY, EXPECTED_VALUE)
        TieredCache.set_all_tiers(TEST_KEY_2, EXPECTED_VALUE)
        TieredCache.delete_all_tiers(TEST_KEY)
        self.assertTrue(self.request_cache.get_cached_response(TEST_KEY).is_miss)
        self.assertEqual(self.request_cache.get_cached_response(TEST_KEY_2).value, EXPECTED_VALUE)
        mock_cache_delete.assert_called_with(TEST_KEY)


class CacheResponseTests(TestCase):
    def test_is_miss(self):
        is_miss = True
        cached_response = CachedResponse(is_miss, EXPECTED_VALUE)
        self.assertTrue(cached_response.is_miss)
        self.assertFalse(cached_response.is_hit)
        with self.assertRaises(CachedResponseError):
            cached_response.value  # pylint: disable=pointless-statement
        self.assertEqual(cached_response.__repr__(), 'CachedResponse (is_hit=False)')

    def test_is_hit(self):
        is_miss = False
        cached_response = CachedResponse(is_miss, EXPECTED_VALUE)
        self.assertFalse(cached_response.is_miss)
        self.assertTrue(cached_response.is_hit)
        self.assertEqual(cached_response.value, EXPECTED_VALUE)
        self.assertEqual(cached_response.__repr__(), 'CachedResponse (is_hit=True)')

    def test_cached_response_misuse(self):
        cached_response = CachedResponse(False, EXPECTED_VALUE)

        with self.assertRaises(CachedResponseError):
            bool(cached_response)

        with self.assertRaises(CachedResponseError):
            # For Python 3
            cached_response.__bool__()

        with self.assertRaises(CachedResponseError):
            cached_response.get('x')

        with self.assertRaises(CachedResponseError):
            cached_response.x = None

        with self.assertRaises(CachedResponseError):
            cached_response['key']  # pylint: disable=pointless-statement

        with self.assertRaises(CachedResponseError):
            cached_response['key'] = None

        with self.assertRaises(CachedResponseError):
            ['a list'][cached_response]  # pylint: disable=expression-not-assigned, pointless-statement

        with self.assertRaises(CachedResponseError):
            'x' in cached_response  # pylint: disable=pointless-statement

        with self.assertRaises(CachedResponseError):
            for x in cached_response:  # pylint: disable=unused-variable
                pass
