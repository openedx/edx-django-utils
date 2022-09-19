"""
Public API for determining the IP address of a request.

Summary
=======

For developers:

- Call ``get_safest_client_ip`` whenever you want to know the caller's IP address
- Make sure ``init_client_ips`` is called as early as possible in the middleware stack
- See the "Guidance for developers" section for more advanced usage

For site operators:

- See the "Configuration" section for important information and guidance

For everyone:

- Background information is available in the "Concepts" section


Concepts
========

- The *IP chain* is the list of IPs in the ``X-Forwarded-For`` (XFF) header followed
  by the ``REMOTE_ADDR`` value. If all involved parties are telling the truth, this
  is the list of IP addresses that have relayed the HTTP request. However, due to
  the possibility of spoofing, this raw data cannot be used directly for all
  purposes:

  - The rightmost IP in the chain is the IP that has directly connected with the
    server and sent or relayed the request. In most deployments, this is likely
    to be a reverse proxy such as nginx. In any case it is the "closest" IP (in
    the sense of the request chain, not in terms of geographic proximity.)
  - The next closest IP, if present, is the one that the closest IP *claims*
    sent the request to it. Each IP in the chain can only vouch for the
    correctness of the IP immediately to its left in the list.
  - In a normal, unspoofed request, the leftmost IP is the "real" client IP, the
    IP of the computer that made the original request.
  - However, clients can send a fake XFF header, so the leftmost IP in the chain
    cannot be trusted in the general case. In fact, the only IP that can be
    trusted absolutely is the rightmost one.
  - The challenge is to determine what the leftmost *trusted* IP is, as this is
    the most accurate we can get without compromising on security.

- The *external chain* is some prefix of the IP chain that stops before the
  (recognized) edge of the deployment's infrastructure. That is, the external
  chain is the portion of the IP chain that is to the left of some trust
  boundary, as determined by configuration or some fallback method. This is the
  list of IPs that can all plausibly be considered the "real" IP of the client.
  If the server is configured correctly this may contain, in order: Any IPs
  spoofed by the client, the client's own IP, IPs of any forwarding HTTP proxies
  specified by the client, and then IPs of any reverse HTTP proxies the
  request passed through *before* reaching the deployment's own infrastructure
  (CDN, load balancer, etc.)

  - Caveat: In the case where the request is being sent through an anonymizing
    proxy such as a VPN, the VPN's exit node IP is considered the "real" client
    IP.
  - Despite the name, this chain may contain private-range IP addresses, in
    particular if a request originates from another server in the same
    datacenter.


Guidance for developers
=======================

Almost anywhere you care about IP address, just call ``get_safest_client_ip``.
This will get you the *rightmost* IP of the external chain (defined above).
Because it cannot be easily spoofed by the caller, it is suitable for adversarial
use-cases such as:

- Rate-limiting
- Only allowing certain IPs to access a resource (or alternatively, blocking them)

In some less common situations where you need the entire external chain, you
can call ``get_all_client_ips`. This returns a list of IP addresses, although for
the great majority of normal requests this will be a list of length 1. This list is
appropriate for when you're recording IPs for manual review or need to make a
decision based on all of the IPs (no matter which one is the "real" one. This might
include:

- Audit logs
- Telling a user about other active sessions on their account
- Georestriction

In some very rare cases you might want just a single IP that isn't rightmost. In
some cases you might ask for the entire external chain and then take the leftmost
IP. This should only be used in non-adversarial situations, and is usually the wrong
choice, but may be appropriate for:

- Localization (if other HTTP headers aren't sufficient)
- Analytics


Configuration
=============

Configuration is via ``CLOSEST_CLIENT_IP_FROM_HEADERS``, which allows specifying
an HTTP header that will be trusted to report the rightmost IP in the external chain.
See setting annotation for details, but guidance on common configurations is provided
here:

- If you use a CDN as your outermost proxy:

  - Find what header your CDN sends to its origin that indicates the remote address it
    sees on inbound connections. For example, with Cloudflare this is ``CF-Connecting-IP``.
  - Ensure that your CDN always overrides this header if it exists in the inbound request,
    and never accepts a value provided by the client. Some CDNs are better than others
    about this.
  - Recommended setting, using Cloudflare as the example::

       CLOSEST_CLIENT_IP_FROM_HEADERS:
       - name: CF-Connecting-IP
         index: 0

    It would be equivalent to use ``-1`` as the index since there is always one and only
    one IP in this header, and Python list indexing rules are used here.
  - As a general rule, you should also ensure that traffic cannot bypass the CDN and reach
    your origin directly, since otherwise attackers will be able to spoof their IP address
    (and bypass protections your CDN provides). You may need to arrange for your CDN to set
    a header containing a shared secret.

- If your outermost proxy is an AWS ELB or other proxy on the same local network as your
  server, or you have any other configuration in which your proxies and application speak
  to each other using private-range IP addresses:

    - You can rely on the rightmost public IP in the IP chain to be the safest client IP.
      To do this, set your configuration for zero trusted headers::

         CLOSEST_CLIENT_IP_FROM_HEADERS: []

    - This assumes that 1) your outermost proxy always appends to ``X-Forwarded-For``, and
      2) any further proxies between that one and your application either append to it
      (ideal) or pass it along unchanged (not ideal, but workable). This is true by default
      for most proxy software.

- If you have any reverse proxy that will be seen by the next proxy or your application as
  having a public IP:

  - You'll need to rely on having a consistent *number* of proxies in front of your
    application, and you'll need to know which ones append to the ``X-Forwarded-For``
    header instead of just passing it unchanged.
  - Once you know the number of your proxies in the chain that append, you can use this
    count to say that the Nth-from-last IP in the ``X-Forwarded-For`` is the closest client
    IP. For example, if you had two, you would use ``-2`` (note the negative sign) to
    indicate the second-from-last IP::

       CLOSEST_CLIENT_IP_FROM_HEADERS:
       - name: X-Forwarded-For
         index: -2

  - This is fragile in the face of network configuration changes, so having your outermost
    proxy set a special header is preferred.
  - Configuring the proxy count too low will result in rate-limiting your own proxies;
    configuring it too high will allow attackers to bypass rate-limiting.
  - Side note: Even if you don't use it for ``CLOSEST_CLIENT_IP_FROM_HEADERS``, this
    proxy-counting approach will be required for configuring django-rest-framework's
    ``NUM_PROXIES`` setting.

- If your application is directly exposed to the public internet, without even a local proxy:

  - This is an unusual configuration, but simple to configure; with no proxies, just indicate
    that there are no trusted headers and therefore the closest public IP should be used::

       CLOSEST_CLIENT_IP_FROM_HEADERS: []
"""

from .internal.ip import get_all_client_ips, get_raw_ip_chain, get_safest_client_ip, init_client_ips
