class AttendanceException(Exception):
    """Base attendance exception."""
    pass


class InvalidAttendanceRequest(AttendanceException):
    """Invalid attendance input."""
    pass


class ShiftNotAssignedException(AttendanceException):
    """Employee has no assigned shift."""
    pass


class AttendanceAlreadyExists(AttendanceException):
    """Duplicate attendance action."""
    pass