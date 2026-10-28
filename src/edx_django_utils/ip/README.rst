IP Address Utils
################

Utilities for safely and correctly determining the IP address(es) of a request.

See ``edx_django_utils/ip/__init__.py`` for documentation and a list of everything included in the public API.

Usage
*****

The short version:

1. Configure ``CLOSEST_CLIENT_IP_FROM_HEADERS``
2. Make sure ``init_client_ips`` is called as early as possible in your middleware stack
3. Call ``get_safest_client_ip`` whenever you want to know the caller's IP address

For details, see ``__init__.py`` module docstring.
