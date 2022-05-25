"""
Cookie consent public API.

See README.rst for details.
"""
from .internal.core import (
    ConsentSource, AcceptAll, OnlyNecessary, OneTrustSource,
    has_consented,
)
