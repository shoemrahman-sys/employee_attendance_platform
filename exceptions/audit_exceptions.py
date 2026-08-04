class AuditException(Exception):
    """Base audit exception."""
    pass


class InvalidAuditRequest(AuditException):
    """Invalid audit log data."""
    pass