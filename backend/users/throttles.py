from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    """Max 5 login attempts per minute per IP."""
    scope = "login"


class RegisterRateThrottle(AnonRateThrottle):
    """Max 10 register attempts per hour per IP."""
    scope = "register"