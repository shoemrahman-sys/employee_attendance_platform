from datetime import date
from repositories.leave_repository import (
    create_leave_request,
    get_employee_leave_requests,
    get_all_leave_requests,
    update_leave_status,
    get_leave_summary,
    get_employee_leave_summary,
    get_approved_leave_for_date
)

from services.audit_service import log_action


def apply_leave(employee_id, leave_type, start_date, end_date, reason):
    if not employee_id:
        return False, "Employee ID is missing."

    if not leave_type or not start_date or not end_date:
        return False, "Please fill all required leave fields."

    if start_date > end_date:
        return False, "Start date cannot be after end date."

    if start_date < date.today():
        return False, "Leave start date cannot be in the past."

    if not reason or reason.strip() == "":
        return False, "Please provide a reason for leave."

    leave_days = (end_date - start_date).days + 1

    if leave_days > 15:
        return False, "Leave duration cannot be more than 15 days."

    existing_leaves = get_employee_leave_requests(employee_id)

    for leave in existing_leaves:
        if leave["status"] in ["Pending", "Approved"]:
            existing_start = leave["start_date"]
            existing_end = leave["end_date"]

            if start_date <= existing_end and end_date >= existing_start:
                return False, "You already have a pending or approved leave request in this date range."

    create_leave_request(
        employee_id=employee_id,
        leave_type=leave_type,
        start_date=start_date,
        end_date=end_date,
        reason=reason
    )

    log_action(
        performed_by=employee_id,
        target_employee_id=employee_id,
        action="Leave Applied",
        description=f"Employee applied for {leave_type} leave from {start_date} to {end_date}."
    )

    return True, "Leave request submitted successfully."


def get_my_leave_history(employee_id):
    return get_employee_leave_requests(employee_id)


def get_leave_requests_for_admin():
    return get_all_leave_requests()


def approve_leave(leave_id, admin_id, employee_id, admin_comment=None):
    update_leave_status(
        leave_id=leave_id,
        status="Approved",
        reviewed_by=admin_id,
        admin_comment=admin_comment
    )

    log_action(
        performed_by=admin_id,
        target_employee_id=employee_id,
        action="Leave Approved",
        description=f"Leave request {leave_id} approved."
    )

    return True, "Leave approved successfully."


def reject_leave(leave_id, admin_id, employee_id, admin_comment=None):
    update_leave_status(
        leave_id=leave_id,
        status="Rejected",
        reviewed_by=admin_id,
        admin_comment=admin_comment
    )

    log_action(
        performed_by=admin_id,
        target_employee_id=employee_id,
        action="Leave Rejected",
        description=f"Leave request {leave_id} rejected."
    )

    return True, "Leave rejected successfully."

def get_leave_kpis():
    return get_leave_summary()

def get_my_leave_kpis(employee_id):
    return get_employee_leave_summary(employee_id)

def is_employee_on_leave(employee_id, target_date):
    leave = get_approved_leave_for_date(employee_id, target_date)
    return leave is not None