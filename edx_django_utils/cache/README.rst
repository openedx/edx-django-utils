Cache Utils
===========

Cache utilities that implement `OEP-0022: Caching in Django`_.

.. _`OEP-0022: Caching in Django`: https://github.com/openedx/open-edx-proposals/blob/master/oeps/oep-0022-bp-django-caches.rst

get_cache_key
-------------

A function for easily creating cache keys.  See its docstring for details.

RequestCache
------------

A thread-local for storing request scoped cache values.

An optional namespace can be used with the RequestCache, or you can use the `DEFAULT_REQUEST_CACHE`.

RequestCacheMiddleware
----------------------

You must include 'edx_django_utils.cache.middleware.RequestCacheMiddleware' when using the RequestCache to ensure it is emptied between requests. This should be added before most middleware, in case any other middleware wants to use the request cache.

Note: This middleware may just be a safety net, but safe is good.

TieredCache
-----------

The first tier is the default request cache that is tied to the life of a given request. The second tier is the Django cache -- e.g. the "default" entry in settings.CACHES, typically backed by memcached.

Some baseline rules:

1. Treat it as a global namespace, like any other cache. The per-request local cache is only going to live for the lifetime of one request, but the backing cache is going to be something like Memcached, where key collision is possible.

2. Timeouts are ignored for the purposes of the in-memory request cache, but do apply to the Django cache. One consequence of this is that sending an explicit timeout of 0 in `set_all_tiers` will cause that item to only be cached across the duration of the request and will not cause a write to the remote cache.

Sample Usage (cache hit)::

    x_cached_response = TieredCache.get_cached_response(key)
    if x_cached_response.is_found:
        return x_cached_response.value
     # calculate x, set in cache, and return value.

Sample Usage (cache miss)::

    x_cached_response = TieredCache.get_cached_response(key)
    if not x_cached_response.is_found:
        # calculate x, set in cache, and return value.
    return x_cached_response.value

Warning when storing bools
^^^^^^^^^^^^^^^^^^^^^^^^^^

**Warning**: When storing a bool in a TieredCache that uses Memcached, `Memcached will return an int`_. However, the RequestCache will return a bool. Therefore, the first time a bool is set the TieredCache will return a bool and in later requests the TieredCache will return an int.

Where possible, you can ensure a consistent return value by storing ``int(my_bool)`` rather than ``my_bool``.

Additionally, when checking the value, do the following check that works for ints::

    # do this.
    if my_bool_cached_response.is_found:
        if my_bool_cached_response.value:
            ...

Do **not** explictly test against ``True`` or ``False``::

    # do NOT do this.
    if my_bool_cached_response.is_found:
        if my_bool_cached_response.value is True:
            ...

.. _Memcached will return an int: https://stackoverflow.com/questions/8169001/why-is-bool-a-subclass-of-int

TieredCacheMiddleware
---------------------

You must include 'edx_django_utils.cache.middleware.TieredCacheMiddleware' when using the TieredCache if you want to enable the `Force Django Cache Miss`_ functionality.

This middleware should come after the required RequestCacheMiddleware, which the TieredCache needs because it uses RequestCache internally. Additionally, since this functionality checks for staff permissions, it should come after any authentication middleware.  Here is an example::

    MIDDLEWARE = (
        'edx_django_utils.cache.middleware.RequestCacheMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        ...
        # TieredCacheMiddleware middleware must come after these.
        'edx_django_utils.cache.middleware.TieredCacheMiddleware',
    )

Force Django Cache Miss
^^^^^^^^^^^^^^^^^^^^^^^

To force recompute a value stored in the django cache, add the query parameter 'force_cache_miss'. This will force a CACHE_MISS.

This requires staff permissions.

Example::

    http://clobert.com/api/v1/resource?force_cache_miss=true


CachedResponse
--------------

A CachedResponse includes the cache miss/hit status (is_found) and the value stored in the cache (for cache hits).

The purpose of the CachedResponse is to avoid a common bug with the default Django cache interface where a cache hit that is Falsey (e.g. None) is misinterpreted as a cache miss.

An example of the Bug::

    # DON'T DO THIS!
    cache_value = cache.get(key)
    if cache_value:
        # calculated value is None, set None in cache, and return value.
        # BUG: None will be treated as a cache miss every time.
    return  cache_value

Future Ideas
------------

* See `ARCH-240`_ for a discussion of additional cache utilities that could be made available.

.. _ARCH-240: https://openedx.atlassian.net/browse/ARCH-240
