"""
Utilities for monitoring code_owner
"""
import logging
import re

from django.conf import settings

log = logging.getLogger(__name__)


def get_code_owner_from_module(module):
    """
    Attempts lookup of code_owner based on a code module,
    finding the most specific match. If no match, returns None.

    For example, if the module were 'openedx.features.discounts.views',
    this lookup would match on 'openedx.features.discounts' before
    'openedx.features', because the former is more specific.

    See how to:
    https://github.com/edx/edx-django-utils/blob/master/edx_django_utils/monitoring/docs/how_tos/add_code_owner_custom_attribute_to_an_ida.rst

    """
    code_owner_mappings = get_code_owner_mappings()
    if code_owner_mappings is None:
        return None

    module_parts = module.split('.')
    # To make the most specific match, start with the max number of parts
    for number_of_parts in range(len(module_parts), 0, -1):
        partial_path = '.'.join(module_parts[0:number_of_parts])
        if partial_path in code_owner_mappings:
            code_owner = code_owner_mappings[partial_path]
            return code_owner
    return None


def is_code_owner_mappings_configured():
    """
    Returns True if code owner mappings were configured, and False otherwise.
    """
    return isinstance(get_code_owner_mappings(), dict)


# cached lookup table for code owner given a module path.
# do not access this directly, but instead use get_code_owner_mappings.
_PATH_TO_CODE_OWNER_MAPPINGS = None


def get_code_owner_mappings():
    """
    Returns the contents of the CODE_OWNER_MAPPINGS Django Setting, processed
    for efficient lookup by path.

    Returns:
         (dict): dict mapping modules to code owners, or None if there are no
            configured mappings, or an empty dict if there is an error processing
            the setting.

    Example return value::

        {
            'xblock_django': 'team-red',
            'openedx.core.djangoapps.xblock': 'team-red',
            'badges': 'team-blue',
        }

    """
    global _PATH_TO_CODE_OWNER_MAPPINGS

    # Return cached processed mappings if already processed
    if _PATH_TO_CODE_OWNER_MAPPINGS is not None:
        return _PATH_TO_CODE_OWNER_MAPPINGS

    # Uses temporary variable to build mappings to avoid multi-threading issue with a partially
    # processed map.  Worst case, it is processed more than once at start-up.
    path_to_code_owner_mapping = {}

    # .. setting_name: CODE_OWNER_MAPPINGS
    # .. setting_default: None
    # .. setting_description: Used for monitoring and reporting of ownership. Use a
    #      dict with keys of code owner name and value as a list of dotted path
    #      module names owned by the code owner.
    code_owner_mappings = getattr(settings, 'CODE_OWNER_MAPPINGS', None)
    if code_owner_mappings is None:
        return None

    try:
        for code_owner in code_owner_mappings:
            path_list = code_owner_mappings[code_owner]
            for path in path_list:
                path_to_code_owner_mapping[path] = code_owner
                optional_module_prefix_match = _OPTIONAL_MODULE_PREFIX_PATTERN.match(path)
                # if path has an optional prefix, also add the module name without the prefix
                if optional_module_prefix_match:
                    path_without_prefix = path[optional_module_prefix_match.end():]
                    path_to_code_owner_mapping[path_without_prefix] = code_owner
    except Exception as e:  # pylint: disable=broad-except
        log.exception('Error processing code_owner_mappings. {}'.format(e))

    _PATH_TO_CODE_OWNER_MAPPINGS = path_to_code_owner_mapping
    return _PATH_TO_CODE_OWNER_MAPPINGS


def clear_cached_mappings():
    """
    Clears the cached path to code owner mappings. Useful for testing.
    """
    global _PATH_TO_CODE_OWNER_MAPPINGS
    _PATH_TO_CODE_OWNER_MAPPINGS = None


# TODO: Remove this LMS specific configuration by replacing with a Django Setting named
#    CODE_OWNER_OPTIONAL_MODULE_PREFIXES that takes a list of module prefixes (without the final period).
_OPTIONAL_MODULE_PREFIX_PATTERN = re.compile(r'^(lms|common|openedx\.core)\.djangoapps\.')
