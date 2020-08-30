"""
Metrics utilities public api

See README.rst for details.
"""
from .transactions import function_trace, get_current_transaction, ignore_transaction, set_monitoring_transaction_name
# "set_custom_metric*" methods are deprecated
from .utils import (
    accumulate,
    increment,
    set_custom_attribute,
    set_custom_attributes_for_course_key,
    set_custom_metric,
    set_custom_metrics_for_course_key
)
