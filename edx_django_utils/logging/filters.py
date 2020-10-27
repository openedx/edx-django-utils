"""
Django-based logging filters

UserIdFilter: A logging.Filter that adds userid to the logging context

RemoteIpFilter: A logging filter that adds the remote IP to the logging context
"""


from logging import Filter

from crum import get_current_request
from crum import get_current_user


class UserIdFilter(Filter):
    """
    Applies a filter to a record to extract the user id from the
    request context.
    """
    def filter(self, record):
        user = get_current_user()
        if user and user.pk:
            record.userid = user.pk
        else:
            record.userid = None
        return True


class RemoteIpFilter(Filter):
    """
    Applies a filter to a record to extract the remote ip from the
    request context.
    """
    def filter(self, record):
        request = get_current_request()
        if request and 'REMOTE_ADDR' in request.META:
            record.remoteip = request.META['REMOTE_ADDR']
        else:
            record.remoteip = None
        return True
