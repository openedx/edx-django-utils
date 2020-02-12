"""
Caching utility middleware.
"""
from django.utils.deprecation import MiddlewareMixin

from edx_django_utils.private_utils import _check_middleware_dependencies

from . import RequestCache, TieredCache


class RequestCacheMiddleware(MiddlewareMixin):
    """
    Middleware to clear the request cache as appropriate for new requests.
    """
    def process_request(self, request):
        """
        Clears the request cache before processing the request.
        """
        RequestCache.clear_all_namespaces()

    def process_response(self, request, response):
        """
         Clear the request cache after processing a response.
         """
        RequestCache.clear_all_namespaces()
        return response

    def process_exception(self, request, exception):
        """
        Clear the request cache after a failed request.
        """
        RequestCache.clear_all_namespaces()


class TieredCacheMiddleware(MiddlewareMixin):
    """
    Middleware to store whether or not to force django cache misses.
    """
    def __init__(self, get_response=None):
        super(TieredCacheMiddleware, self).__init__(get_response=get_response)
        # checks proper dependency order as well.
        _check_middleware_dependencies(self, required_middleware=[
            'edx_django_utils.cache.middleware.RequestCacheMiddleware',
            # Some Authentication Middleware also needs to be in between,
            # but don't want to hard-code that dependency.
            'edx_django_utils.cache.middleware.TieredCacheMiddleware',
        ])

    def process_request(self, request):
        """
        Stores whether or not FORCE_CACHE_MISS_PARAM was supplied in the
        request.
        """
        TieredCache._get_and_set_force_cache_miss(request)  # pylint: disable=protected-access
