"""
User cache utilities.
"""
import logging

from edx_django_utils.cache import TieredCache, get_cache_key
from edx_django_utils.monitoring import set_custom_metric

log = logging.getLogger(__name__)


class CachedAuthenticatedUserDetails():
    """
    Enables caching authenticated user details for a request, avoiding the need to
    store the data in the database, which is especially useful for PII (Personally
    Identifiable Information).

    """
    def __init__(self, user_id):
        """
        Arguments:
            user_id: Pass in user.id.
        """
        assert user_id, 'The user.id must be supplied.'
        self.user_id = user_id

    def _get_authenticated_user_cache_key(self):
        return get_cache_key(
            prefix='edx_django_utils.authenticated_user_details',
            unique_id=self.user_id
        )

    def set_cached_authenticated_user_details(self, display_name):
        """
        Caches details about the authenticated user for use in a request.
        """
        if not display_name:
            log.error("Caching empty display_name.")
        authenticated_user_details = {'display_name': display_name}
        TieredCache.set_all_tiers(self._get_authenticated_user_cache_key(), authenticated_user_details)
        # Temporary metric to ensure display_name is never blank
        set_custom_metric('set_cached_display_name', display_name)

    @property
    def display_name(self):
        """
        Retrieves cached display_name of the authenticated user.
        """
        user_details_cached_response = TieredCache.get_cached_response(self._get_authenticated_user_cache_key())
        if not user_details_cached_response.is_found:
            # Note: There are valid cases where this gets called before the set during SSO.
            return ''

        display_name = user_details_cached_response.value['display_name']
        if not display_name:
            return ''

        return display_name
