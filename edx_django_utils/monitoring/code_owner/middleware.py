"""
Middleware for code_owner custom metric
"""
import logging

from django.urls import resolve

from edx_django_utils.monitoring import get_current_transaction, set_custom_metric

from .utils import get_code_owner_from_module, is_code_owner_mappings_configured

log = logging.getLogger(__name__)


class CodeOwnerMetricMiddleware:
    """
    Django middleware object to set custom metrics for the owner of each view.

    Custom metrics set:
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
        self._set_code_owner_metric(request)
        return response

    def process_exception(self, request, exception):
        self._set_code_owner_metric(request)

    def _set_code_owner_metric(self, request):
        """
        Sets the code_owner custom metric, as well as several supporting custom metrics.

        See CodeOwnerMetricMiddleware docstring for a complete list of metrics.

        """
        code_owner, path_error = self._set_code_owner_metric_from_path(request)
        if code_owner:
            set_custom_metric('code_owner', code_owner)
            return
        if not path_error:
            # module found, but mapping wasn't configured
            return

        code_owner, transaction_error = self._set_code_owner_metric_from_current_transaction(request)
        if code_owner:
            set_custom_metric('code_owner', code_owner)
            return
        if not transaction_error:
            # transaction name found, but mapping wasn't configured
            return

        # only report errors if either code_owner couldn't be found
        if path_error:
            set_custom_metric('code_owner_path_error', path_error)
        if transaction_error:
            set_custom_metric('code_owner_transaction_error', transaction_error)

    def _set_code_owner_metric_from_path(self, request):
        """
        Uses the request path to find the view_func and then sets code owner metrics based on the view.

        Side-effects:
            Sets code_owner_path_module custom metric, used to determine code_owner

        Returns:
            (str, str): (code_owner, error_message), where at least one of these should be None

        """
        if not is_code_owner_mappings_configured():  # pragma: no cover
            return None, None

        try:
            view_func, _, _ = resolve(request.path)
            path_module = view_func.__module__
            set_custom_metric('code_owner_path_module', path_module)
            code_owner = get_code_owner_from_module(path_module)
            return code_owner, None
        except Exception as e:  # pylint: disable=broad-except
            return None, str(e)

    def _set_code_owner_metric_from_current_transaction(self, request):
        """
        Uses the current transaction name to set the code owner metric.

        Side-effects:
            Sets code_owner_transaction_name custom metric, used to determine code_owner

        Returns:
            (str, str): (code_owner, error_message), where at least one of these should be None

        """
        if not is_code_owner_mappings_configured():
            return None, None

        try:
            # Example: openedx.core.djangoapps.contentserver.middleware:StaticContentServer
            transaction_name = get_current_transaction().name
            if not transaction_name:
                return None, 'No current transaction name found.'
            set_custom_metric('code_owner_transaction_name', transaction_name)
            module_name = transaction_name.split(':')[0]
            code_owner = get_code_owner_from_module(module_name)
            return code_owner, None
        except Exception as e:  # pylint: disable=broad-except
            return None, str(e)
