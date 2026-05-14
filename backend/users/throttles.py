import sys
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

TESTING = "pytest" in sys.modules


class LoginRateThrottle(AnonRateThrottle):
    """Max 5 login attempts per minute per IP."""
    scope = "login"

    def allow_request(self, request, view):
        if TESTING:
            return True
        return super().allow_request(request, view)


class RegisterRateThrottle(AnonRateThrottle):
    """Max 10 register attempts per hour per IP."""
    scope = "register"

    def allow_request(self, request, view):
        if TESTING:
            return True
        return super().allow_request(request, view)