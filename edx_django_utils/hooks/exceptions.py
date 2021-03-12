"""
Exceptions thrown by Hooks.
"""


class HookException(Exception):
    """
    Base exception for hooks. It is re-raised by the Pipeline Runner if any of
    the actions/filters that is executing raises it.

    Arguments:
        message (str): message describing why the exception was raised.
        redirect_to (str): redirect URL.
        status_code (int): HTTP status code.
        keyword arguments (kwargs): extra arguments used to customize exception.
    """

    def __init__(self, message="", redirect_to=None, status_code=None, **kwargs):
        super().__init__()
        self.message = message
        self.redirect_to = redirect_to
        self.status_code = status_code
        self.kwargs = kwargs

    def __str__(self):
        return "HookException: {}".format(self.message)
