6. Content-Security-Policy middleware
#####################################

Status
******

Provisional (2023-04-07)

Context
*******

2U's Security Working Group is interested in adding the ``Content-Security-Policy`` response header (CSP) to as many edx.org domains as possible, in order to provide a layer of security on top of existing XSS mitigations and security measures. Some other deployers are also likely to be interested in using CSP. (There are also two additional headers ``Content-Security-Policy-Report-Only`` (CSP-RO) and ``Reporting-Endpoints``; together these will be referred to as the "CSP headers".)

``Content-Security-Policy`` is a powerful HTTP response header that can:

- Block XSS, exfiltration, UI redress, and various other kinds of attacks
- Gather reports of violations, allowing deployers to discover vulnerabilities even while CSP prevents them from being exploited
- Enforce the use of a business process for adding new external scripts to the site

At the most basic level, CSP allows the server to tell the browser to refuse to load any Javascript that isn't on an allowlist. More advanced deployments can restrict other kinds of resources (including service workers, child frames, images, and XHR connections). A static set of headers can only support an allowlist that is based on domain names and paths, but features such as ``strict-dynamic`` and ``nonce`` allow the server to vouch for scripts individually. This is more secure but requires more integration with application code.

If fully deployed, there is a reduction of risk to learners, partners, and the site's reputation. However, for full effect, these security headers must be returned on all responses, including non-HTML resources and error pages. CSP headers must also be tailored not only to each IDA and MFE, but to each *deployment*, as different deployers will load images and scripts from different domains.

CSP policies are often very long (1 kB in one example) and are built from a number of directives that each contain an allowlist or configuration. They cannot be loosened by the addition of later headers, but only tightened. This means that the server must return the entire policy in one shot, or alternatively emit some directives as separate headers. The use of ``strict-dynamic`` can shrink the header and make the policy more flexible, but requires integration between body and headers: The headers must either contain hashes of the scripts, or nonces that are also referenced in the HTML.

Microfrontends are generally served from static file hosting such as Amazon S3 and cannot take advantage of ``strict-dynamic``; they are limited to source allowlists set by the fileserver or a CDN. In contrast, Django-based IDAs could use ``strict-dynamic`` (via nonces and hashes) because of the ability to customize header and body contents for each response.

As of April 2023, most MFEs and other IDAs include inline Javascript, which severely limits the protection that CSP can provide. However, an initial deployment of CSP that locks down script source domains to an allowlist and reports on the locations of remaining inline scripts would be a good start towards cleaning up these inline scripts. In other words, the goal here is to get *started* on CSP.

Decision
********

We will add a CSP middleware to edx-django-utils that can attach CSP headers based on Django settings. These will be static values, but with the option for simultaneous use of different CSP and CSP-RO headers, allowing safe rollout of increased restrictions.

We will enable this middleware for all Django-based IDAs.

Consequences
************

Django-based IDAs will for now be restricted to using static headers, and will not support ``strict-dynamic``. This is equivalent in configurability to having a CDN attach headers, and is good enough for a first pass, but will almost certainly need to be replaced with a more integrated system later as IDAs are adjusted to become amenable to ``strict-dynamic``.

Rejected Alternatives
*********************

Configure at the CDN level
==========================

Since the initial version of this is equivalent to CDN headers in flexibility, we could just require that deployers use a CDN (or their origin web server) to attach these headers. This would meet 2U's needs in the short term. However, this would be a move in the wrong direction if we want to support more advanced, easier-to-use configurations in the future such as ``strict-dynamic``. It would also leave each deployer to build their own header-attaching solution.

Attach arbitrary headers
========================

Since the CSP headers are staticly configured, it could be sufficient to make (or install from PyPI) a middleware that just attaches HTTP response headers. However, none were readily available that also appeared suitable.

Additionally, the CSP policies are quite long, and it is preferable to be able to write them in multiline strings with free choice of line breaks and indentation. YAML mostly supports this, but only if *exactly* the right multiline string syntax is used (only 1 of the 9 multiline string forms is appropriate) so this would be error-prone and fragile.

Having custom code not only allows collapsing whitespace runs but also allows trimming a trailing semicolon. CSP headers do not permit trailing delimiters or empty directives, but as seen in many programming languages, allowing trailing delimiters allows for better maintainability. CSP-specific code can remove the final delimiter and make mistakes less likely.

django-csp package
==================

https://github.com/mozilla/django-csp would technically work, and it’s nice that it breaks apart the CSP into pieces that can be separately controlled and even modified by views and middleware. This would immediately allow progress towards ``strict-dynamic`` CSP and even allow view-specific allow-lists. However, it doesn’t allow both CSP and CSP-RO at the same time. This is not a deal-breaker, but it does make deployment harder and somewhat reduces security, as it means that any time a directive is to be tightened the header must be taken out of enforcement mode for some observation period. (It is also not clear whether this library is maintained at this point.)

If this library is at some point changed to support simultaneous use of CSP and CSP-RO, or if another library is developed that has equivalent properties, then it would be appropriate to migrate to using that.

References
**********

- https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy - Overview of CSP and its options
- https://www.w3.org/TR/CSP3/ - Spec that defines CSP
- https://w3c.github.io/reporting/ - Spec that defines the ``Reporting-Endpoints`` header
