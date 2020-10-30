"""
Middleware for code_owner custom attribute
"""
import logging

from django.urls import resolve

from ..transactions import get_current_transaction
from ..utils import set_custom_attribute
from .utils import get_code_owner_from_module, is_code_owner_mappings_configured

log = logging.getLogger(__name__)


class CodeOwnerMonitoringMiddleware:
    """
    Django middleware object to set custom attributes for the owner of each view.

    For instructions on usage, see:
    https://github.com/edx/edx-django-utils/blob/master/edx_django_utils/monitoring/docs/how_tos/add_code_owner_custom_attribute_to_an_ida.rst

    Custom attributes set:
    - code_owner: The owning team mapped to the current view.
    - code_owner_mapping_error: If there are any errors when trying to perform the mapping.
    - code_owner_path_error: The error mapping by path, if code_owner isn't found in other ways.
    - code_owner_path_module: The __module__ of the view_func which was used to try to map to code_owner.
        This can be used to find missing mappings.
    - code_owner_transaction_error: The error mapping by transaction, if code_owner isn't found in other ways.
    - code_owner_transaction_name: The current transaction name used to try to map to code_owner.
        This can be used to find missing mappings.

    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        self._set_code_owner_attribute(request)
        return response

    def process_exception(self, request, exception):
        self._set_code_owner_attribute(request)

    def _set_code_owner_attribute(self, request):
        """
        Sets the code_owner custom attribute, as well as several supporting custom attributes.

        See CodeOwnerMonitoringMiddleware docstring for a complete list of attributes.

        """
        code_owner, path_error = self._set_code_owner_attribute_from_path(request)
        if code_owner:
            set_custom_attribute('code_owner', code_owner)
            return
        if not path_error:
            # module found, but mapping wasn't configured
            code_owner = self._set_code_owner_attribute_catch_all()
            if code_owner:
                set_custom_attribute('code_owner', code_owner)
            return

        code_owner, transaction_error = self._set_code_owner_attribute_from_current_transaction(request)
        if code_owner:
            set_custom_attribute('code_owner', code_owner)
            return
        if not transaction_error:
            # transaction name found, but mapping wasn't configured
            code_owner = self._set_code_owner_attribute_catch_all()
            if code_owner:
                set_custom_attribute('code_owner', code_owner)
            return

        code_owner = self._set_code_owner_attribute_catch_all()
        if code_owner:
            set_custom_attribute('code_owner', code_owner)
            return

        # only report errors if code_owner couldn't be found, including catch-all
        if path_error:
            set_custom_attribute('code_owner_path_error', path_error)
        if transaction_error:
            set_custom_attribute('code_owner_transaction_error', transaction_error)

    def _set_code_owner_attribute_from_path(self, request):
        """
        Uses the request path to find the view_func and then sets code owner attributes based on the view.

        Side-effects:
            Sets code_owner_path_module custom attribute, used to determine code_owner

        Returns:
            (str, str): (code_owner, error_message), where at least one of these should be None

        """
        if not is_code_owner_mappings_configured():
            return None, None

        try:
            view_func, _, _ = resolve(request.path)
            path_module = view_func.__module__
            set_custom_attribute('code_owner_path_module', path_module)
            code_owner = get_code_owner_from_module(path_module)
            return code_owner, None
        except Exception as e:  # pylint: disable=broad-except
            return None, str(e)

    def _set_code_owner_attribute_from_current_transaction(self, request):
        """
        Uses the current transaction name to set the code owner attribute.

        Side-effects:
            Sets code_owner_transaction_name custom attribute, used to determine code_owner

        Returns:
            (str, str): (code_owner, error_message), where at least one of these should be None

        """
        if not is_code_owner_mappings_configured():
            # ensure we don't set code ownership custom attributes if not configured to do so
            return None, None  # pragma: no cover

        try:
            # Example: openedx.core.djangoapps.contentserver.middleware:StaticContentServer
            transaction_name = get_current_transaction().name
            if not transaction_name:
                return None, 'No current transaction name found.'
            module_name = transaction_name.split(':')[0]
            set_custom_attribute('code_owner_transaction_name', transaction_name)
            set_custom_attribute('code_owner_path_module', module_name)
            code_owner = get_code_owner_from_module(module_name)
            return code_owner, None
        except Exception as e:  # pylint: disable=broad-except
            return None, str(e)

    def _set_code_owner_attribute_catch_all(self):
        """
        If the catch-all module "*" is configured, return the code_owner.

        Returns:
            (str): code_owner or None if no catch-all configured.

        """
        try:
            code_owner = get_code_owner_from_module('*')
            return code_owner
        except Exception:  # pylint: disable=broad-except; #pragma: no cover
            return None
