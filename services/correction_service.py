from repositories.correction_repository import (
    create_correction_request,
    get_employee_correction_requests,
    get_all_correction_requests,
    update_correction_status
)

from repositories.attendance_repository import update_attendance_correction
from services.audit_service import log_action


def submit_correction_request(
    employee_id,
    attendance_id,
    requested_check_in,
    requested_check_out,
    reason
):
    if not employee_id:
        return False, "Employee ID missing."

    if not attendance_id:
        return False, "Please select an attendance record."

    if not reason or reason.strip() == "":
        return False, "Please provide a reason."

    if not requested_check_in and not requested_check_out:
        return False, "Please provide requested check-in or check-out time."

    create_correction_request(
        employee_id=employee_id,
        attendance_id=attendance_id,
        requested_check_in=requested_check_in,
        requested_check_out=requested_check_out,
        reason=reason
    )

    log_action(
        performed_by=employee_id,
        target_employee_id=employee_id,
        action="Attendance Correction Requested",
        description=f"Employee requested correction for attendance ID {attendance_id}."
    )

    return True, "Attendance correction request submitted successfully."


def get_my_correction_requests(employee_id):
    return get_employee_correction_requests(employee_id)


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
    update_attendance_correction(
        attendance_id=attendance_id,
        check_in=requested_check_in,
        check_out=requested_check_out
    )

    update_correction_status(
        correction_id=correction_id,
        status="Approved",
        reviewed_by=admin_id,
        admin_comment=admin_comment
    )

    log_action(
        performed_by=admin_id,
        target_employee_id=employee_id,
        action="Attendance Correction Approved",
        description=f"Admin approved correction request {correction_id}."
    )

    return True, "Attendance correction approved successfully."


def reject_correction(
    correction_id,
    admin_id,
    employee_id,
    admin_comment=None
):
    update_correction_status(
        correction_id=correction_id,
        status="Rejected",
        reviewed_by=admin_id,
        admin_comment=admin_comment
    )

    log_action(
        performed_by=admin_id,
        target_employee_id=employee_id,
        action="Attendance Correction Rejected",
        description=f"Admin rejected correction request {correction_id}."
    )

    return True, "Attendance correction rejected successfully."