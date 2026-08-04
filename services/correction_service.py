from config.database import get_transaction_connection
from utils.logger import logger

from repositories.correction_repository import (
    create_correction_request,
    get_employee_correction_requests,
    get_all_correction_requests,
    update_correction_status
)

from repositories.attendance_repository import (
    update_attendance_correction
)

from services.audit_service import log_action

from exceptions.correction_exceptions import (
    InvalidCorrectionRequest,
    CorrectionApprovalException
)


def validate_correction_request(
    employee_id,
    attendance_id,
    requested_check_in,
    requested_check_out,
    reason
):

    if not employee_id:
        raise InvalidCorrectionRequest(
            "Employee ID missing."
        )

    if not attendance_id:
        raise InvalidCorrectionRequest(
            "Please select an attendance record."
        )

    if not reason or reason.strip() == "":
        raise InvalidCorrectionRequest(
            "Please provide a reason."
        )

    if not requested_check_in and not requested_check_out:
        raise InvalidCorrectionRequest(
            "Please provide requested check-in or check-out time."
        )


def validate_correction_action(
    correction_id,
    admin_id,
    employee_id
):

    if not correction_id:
        raise CorrectionApprovalException(
            "Correction ID is required."
        )

    if not admin_id:
        raise CorrectionApprovalException(
            "Admin ID is required."
        )

    if not employee_id:
        raise CorrectionApprovalException(
            "Employee ID is required."
        )


def submit_correction_request(
    employee_id,
    attendance_id,
    requested_check_in,
    requested_check_out,
    reason
):

    try:

        validate_correction_request(
            employee_id,
            attendance_id,
            requested_check_in,
            requested_check_out,
            reason
        )


        create_correction_request(
            employee_id=employee_id,
            attendance_id=attendance_id,
            requested_check_in=requested_check_in,
            requested_check_out=requested_check_out,
            reason=reason
        )


        logger.info(
            "Correction requested: employee_id=%s attendance_id=%s",
            employee_id,
            attendance_id
        )


        log_action(
            performed_by=employee_id,
            target_employee_id=employee_id,
            action="Attendance Correction Requested",
            description=f"Employee requested correction for attendance ID {attendance_id}."
        )


        return True, "Attendance correction request submitted successfully."


    except InvalidCorrectionRequest as e:

        logger.warning(
            "Invalid correction request: employee_id=%s error=%s",
            employee_id,
            str(e)
        )

        return False, str(e)


    except Exception as e:

        logger.error(
            "Correction submission failed: employee_id=%s error=%s",
            employee_id,
            str(e),
            exc_info=True
        )

        return False, "Unable to submit correction request."



def get_my_correction_requests(employee_id):

    return get_employee_correction_requests(
        employee_id
    )



def get_correction_requests_for_admin():

    return get_all_correction_requests()



def approve_correction(
    correction_id,
    admin_id,
    employee_id,
    attendance_id,
    requested_check_in,
    requested_check_out,
    admin_comment=None
):

    conn = None

    try:

        validate_correction_action(
            correction_id,
            admin_id,
            employee_id
        )


        conn = get_transaction_connection()

        conn.start_transaction()


        update_attendance_correction(
            attendance_id=attendance_id,
            check_in=requested_check_in,
            check_out=requested_check_out,
            conn=conn
        )


        update_correction_status(
            correction_id=correction_id,
            status="Approved",
            reviewed_by=admin_id,
            admin_comment=admin_comment,
            conn=conn
        )


        log_action(
            performed_by=admin_id,
            target_employee_id=employee_id,
            action="Attendance Correction Approved",
            description=f"Admin approved correction request {correction_id}.",
            conn=conn
        )


        conn.commit()


        logger.info(
            "Correction approved: correction_id=%s admin=%s",
            correction_id,
            admin_id
        )


        return True, "Attendance correction approved successfully."


    except Exception as e:

        if conn:
            conn.rollback()


        logger.error(
            "Correction approval failed: correction_id=%s error=%s",
            correction_id,
            str(e),
            exc_info=True
        )


        return False, "Unable to approve correction request."


    finally:

        if conn:
            conn.close()



def reject_correction(
    correction_id,
    admin_id,
    employee_id,
    admin_comment=None
):

    conn = None

    try:

        validate_correction_action(
            correction_id,
            admin_id,
            employee_id
        )


        conn = get_transaction_connection()

        conn.start_transaction()


        update_correction_status(
            correction_id=correction_id,
            status="Rejected",
            reviewed_by=admin_id,
            admin_comment=admin_comment,
            conn=conn
        )


        log_action(
            performed_by=admin_id,
            target_employee_id=employee_id,
            action="Attendance Correction Rejected",
            description=f"Admin rejected correction request {correction_id}.",
            conn=conn
        )


        conn.commit()


        logger.info(
            "Correction rejected: correction_id=%s admin=%s",
            correction_id,
            admin_id
        )


        return True, "Attendance correction rejected successfully."


    except Exception as e:

        if conn:
            conn.rollback()


        logger.error(
            "Correction rejection failed: correction_id=%s error=%s",
            correction_id,
            str(e),
            exc_info=True
        )


        return False, "Unable to reject correction request."


    finally:

        if conn:
            conn.close()