"""
Common utility methods for Mobile APIs.
"""
from openedx.core.lib.api.view_utils import view_auth_classes


def mobile_view(is_user=False):
    """
    Function and class decorator that abstracts the authentication and permission checks for mobile api views.
    """
    return view_auth_classes(is_user)


def parsed_version(version):
    """ Converts string X.X.X.Y to int tuple (X, X, X) """
    return tuple(map(int, (version.split(".")[:3])))
