"""
Implementation of ``edx_django_utils.ip`` -- contains non-public
functions, and is subject to breaking changes without warning.

Import from ``edx_django_utils.ip`` instead of this one.
See that module's docstring for additional background.
"""

import ipaddress
import warnings

from django.conf import settings


def _get_meta_ip_strs(request, header_name):
    """
    Get a list of IPs from a header in the given request.

    Return the list of IPs the request is carrying on this header, which is
    expected to be comma-delimited if it contains more than one. Response
    may be an empty list for missing or empty header. List items may not be
    valid IPs.
    """
    header_value = request.headers.get(header_name, '').strip()

    if header_value:
        return [s.strip() for s in header_value.split(',')]
    else:
        return []


def get_raw_ip_chain(request):
    """
    Retrieve the full IP chain from this request, as list of raw strings.

    This is uninterpreted and unparsed, except for splitting on commas and
    removing extraneous whitespace.
    """
    return _get_meta_ip_strs(request, 'X-Forwarded-For') + [request.META['REMOTE_ADDR']]


def _get_usable_ip_chain(request):
    """
    Retrieve the full IP chain from this request, as parsed addresses.

    The IP chain is the X-Forwarded-For header, followed by the REMOTE_ADDR.
    This list is then narrowed to the largest suffix that can be parsed as
    IP addresses.
    """
    parsed = []
    for ip_str in reversed(get_raw_ip_chain(request)):
        try:
            parsed.append(ipaddress.ip_address(ip_str))
        except ValueError:
            break
    return list(reversed(parsed))


def _remove_tail(elements, f_discard):
    """
    Remove items from the tail of the given list until f_discard returns false.

    - elements is a list
    - f_discard is a function that accepts an item from the list and returns
      true if it should be discarded from the tail

    Returns a new list that is a possibly-empty prefix of the input list.

    (This is basically itertools.dropwhile on a reversed list.)
    """
    prefix = elements[:]
    while prefix and f_discard(prefix[-1]):
        prefix.pop()
    return prefix


def _get_client_ips_via_xff(request):
    """
    Get the external chain of the request by discarding private IPs.

    This is a strategy used by ``get_all_client_ips`` and should not be used
    directly.

    Returns a list of *parsed* IP addresses, one of:

    - A list ending in a publicly routable IP
    - A list with a single, private-range IP
    - An empty list, if REMOTE_ADDR was unparseable as an IP address. This
      would be very unusual but could possibly happen if a local reverse proxy
      used a domain socket rather than a TCP connection.
    """
    ip_chain = _get_usable_ip_chain(request)
    external_chain = _remove_tail(ip_chain, lambda ip: not ip.is_global)

    # If the external_chain is in fact all private, everything will have been
    # removed. In that case, just return the leftmost IP it would have
    # considered, even though it must be a private IP.
    return external_chain or ip_chain[:1]


# .. setting_name: CLOSEST_CLIENT_IP_FROM_HEADERS
# .. setting_default: []
# .. setting_description: A list of header/index pairs to use for determining the IP in the
#   IP chain that is just outside of this deployment's infrastructure boundary -- that is,
#   the rightmost address in the IP chain that is *not* owned by the deployment. (See module
#   docstring for background and definitions, as well as guidance on configuration.)
#       Each list entry is a dict containing a header name and an index into that header. This will
#   control how the client's IP addresses are determined for attribution, tracking, rate-limiting,
#   or other general-purpose needs.
#       The named header must contain a list of IP addresses separated by commas, with whitespace
#   tolerated around each address. The index is used for a Python list lookup, e.g. 0 is the first
#   element and -2 is the second from the end.
#       Header/index pairs will be tried in turn until the first one that yields a usable IP, which
#   will then be used to determine the end of the external chain.
#       If the setting is an empty list, or if none of the entries yields a usable IP (header is
#   missing, index out of range, IP not in IP chain), then a fallback strategy will be used
#   instead: Private-range IPs will be discarded from the right of the IP chain until a public
#   IP is found, or the chain shrinks to one IP. This entry will then be considered the rightmost
#   end of the external chain.
#       Migrations from one network configuration to another may be accomplished by first adding the
#   new header to the list, making the networking change, and then removing the old one.
# .. setting_warnings: Changes to the networking configuration that are not coordinated with
#   this setting may allow callers to spoof their IP address.


def _get_trusted_header_ip(request, header_name, index):
    """
    Read a parsed IP address from a header at the specified position.

    Helper function for ``_get_client_ips_via_trusted_header``.

    Returns None if header is missing, index is out of range, or the located
    entry can't be parsed as an IP address.
    """
    ip_strs = _get_meta_ip_strs(request, header_name)

    if not ip_strs:
        warnings.warn(f"Configured IP address header was missing: {header_name!r}", UserWarning)
        return None

    try:
        trusted_ip_str = ip_strs[index]
    except IndexError:
        warnings.warn(
            "Configured index into IP address header is out of range: "
            f"{header_name!r}:{index!r} "
            f"(actual length {len(ip_strs)})",
            UserWarning
        )
        return None

    try:
        return ipaddress.ip_address(trusted_ip_str)
    except ValueError:
        warnings.warn(
            "Configured trusted IP address header contained invalid IP: "
            f"{header_name!r}:{index!r}",
            UserWarning
        )
        return None


def _get_client_ips_via_trusted_header(request) -> list:
    """
    Get the external chain by reading the trust boundary from a header.

    This is a strategy used by ``get_all_client_ips`` and should not be used
    directly. It does not implement any fallback in case of misconfiguration.

    Uses ``CLOSEST_CLIENT_IP_FROM_HEADERS`` to identify the IP just outside of
    the deployment's infrastructure boundary, and uses the rightmost position
    of this to determine where the external chain stops. See setting docs for
    more details.

    Returns one of the following:

    - A non-empty list of *parsed* IP addresses, where the rightmost IP is the
      same as the one identified in the trusted header.
    - Empty list if no headers configured or all headers are unusable.

    A configured header can be unusable if it's missing from the request, the
    index is out of range, the indicated entry in the header can't be parsed
    as an IP address, or the IP in the header can't be found in the IP chain.
    """
    header_entries = getattr(settings, 'CLOSEST_CLIENT_IP_FROM_HEADERS', [])

    full_chain = _get_usable_ip_chain(request)
    external_chain = []

    for entry in header_entries:
        header_name = entry['name']
        index = entry['index']
        if closest_client_ip := _get_trusted_header_ip(request, header_name, index):
            # The equality check in this predicate is why we use parsed IP
            # addresses -- ::1 should compare as equal to 0:0:0:0:0:0:0:1.
            external_chain = _remove_tail(full_chain, lambda ip: ip != closest_client_ip)  # pylint: disable=cell-var-from-loop
            if external_chain:
                break

            warnings.warn(
                f"Ignoring trusted header IP {header_name!r}:{index!r} "
                "because it was not found in the actual IP chain.",
                UserWarning
            )

    return external_chain


def _compute_client_ips(request):
    """
    Get the request's external chain, a non-empty list of IP address strings.

    Warning: should only be called once and cached by ``init_client_ips``.

    Prefer to use ``get_all_client_ips`` to retrieve the value stored on the
    request, unless you are sure that later middleware has not modified
    the REMOTE_ADDR in-place.

    This function will attempt several strategies to determine the external chain:

    - If ``CLOSEST_CLIENT_IP_FROM_HEADERS`` is configured and usable, it will be
      used to determine the rightmost end of the external chain (by reading a
      trusted HTTP header).
    - If that does not yield a result, fall back to assuming that the rightmost
      public IP address in the IP chain is the end of the external chain. (For an
      in-datacenter HTTP request, may instead yield a list with a private IP.)
    """
    # In practice the fallback to REMOTE_ADDR should never happen, since that
    # would require that value to be present and malformed but with no XFF
    # present.
    ips = _get_client_ips_via_trusted_header(request) \
        or _get_client_ips_via_xff(request) \
        or [request.META['REMOTE_ADDR']]

    return [str(ip) for ip in ips]


def init_client_ips(request):
    """
    Compute the request's external chain and store it in the request.

    This should be called early in the middleware stack in order to avoid
    being called after another middleware that overwrites ``REMOTE_ADDR``,
    which is a pattern some apps use.

    If called multiple times or if ``CLIENT_IPS`` is already present in
    ``request.META``, will just warn.
    """
    if 'CLIENT_IPS' in request.META:
        warnings.warn("init_client_ips refusing to overwrite existing CLIENT_IPS")
    else:
        request.META['CLIENT_IPS'] = _compute_client_ips(request)


def get_all_client_ips(request):
    """
    Get the request's external chain, a non-empty list of IP address strings.

    Most consumers of IP addresses should just use ``get_safest_client_ip``.

    Calls ``init_client_ips`` if needed.
    """
    if 'CLIENT_IPS' not in request.META:
        init_client_ips(request)

    return request.META['CLIENT_IPS']


def get_safest_client_ip(request):
    """
    Get the safest choice of client IP.

    Returns a single string containing the IP address that most likely
    represents the originator of the HTTP call, without compromising on
    safety.

    This is always the rightmost value in the external IP chain that
    is returned by ``get_all_client_ips``. See module docstring for
    more details.
    """
    return get_all_client_ips(request)[-1]
