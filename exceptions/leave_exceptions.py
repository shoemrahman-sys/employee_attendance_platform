class LeaveException(Exception):
    """Base exception for leave-related errors."""
    pass


class InvalidLeaveRequest(LeaveException):
    """Raised when leave input validation fails."""
    pass


class LeaveOverlapException(LeaveException):
    """Raised when employee already has overlapping leave."""
    pass


class LeaveApprovalException(LeaveException):
    """Raised when leave approval/rejection fails."""
    pass