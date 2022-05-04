Logging Utils
=============

Several utilities for assisting with logging.

See ``__init__.py`` for a list of everything included in the public API.

Logging filters
---------------

- ``RemoteIpFilter``: A logging filter that adds the remote IP to the logging context
- ``UserIdFilter``: A logging filter that adds userid to the logging context

Logging of sensitive information
--------------------------------

``encrypt_for_log`` allows encrypting a string in a way appropriate for logging. See module docstring for more information.

This package also exposes a CLI command ``log_sensitive`` for key generation and decryption.
