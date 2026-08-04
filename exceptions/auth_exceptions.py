class AuthException(Exception):
    """Base authentication exception."""
    pass


class InvalidRegistration(AuthException):
    pass


class InvalidLogin(AuthException):
    pass


class AccountLocked(AuthException):
    pass


class PasswordResetException(AuthException):
    pass