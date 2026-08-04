class CorrectionException(Exception):
    """Base correction exception."""
    pass


class InvalidCorrectionRequest(CorrectionException):
    """Invalid correction input."""
    pass


class CorrectionNotFound(CorrectionException):
    """Correction record not found."""
    pass


class CorrectionApprovalException(CorrectionException):
    """Correction approval/rejection failed."""
    pass