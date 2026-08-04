from datetime import date

from utils.logger import logger

from config.database import get_transaction_connection

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

from exceptions.leave_exceptions import (
    InvalidLeaveRequest,
    LeaveOverlapException,
    LeaveApprovalException
)


def validate_leave_request(
    employee_id,
    leave_type,
    start_date,
    end_date,
    reason
):
    """
    Validate employee leave application details.
    """

    if not employee_id:
        raise InvalidLeaveRequest(
            "Employee ID is missing."
        )

    if not leave_type or not start_date or not end_date:
        raise InvalidLeaveRequest(
            "Please fill all required leave fields."
        )

    if start_date > end_date:
        raise InvalidLeaveRequest(
            "Start date cannot be after end date."
        )

    if start_date < date.today():
        raise InvalidLeaveRequest(
            "Leave start date cannot be in the past."
        )

    if not reason or reason.strip() == "":
        raise InvalidLeaveRequest(
            "Please provide a reason for leave."
        )

    leave_days = (end_date - start_date).days + 1

    if leave_days > 15:
        raise InvalidLeaveRequest(
            "Leave duration cannot be more than 15 days."
        )


def validate_leave_action(
    leave_id,
    admin_id,
    employee_id
):
    """
    Validate admin leave approval/rejection action.
    """

    if not leave_id:
        raise LeaveApprovalException(
            "Leave ID is required."
        )

    if not admin_id:
        raise LeaveApprovalException(
            "Admin ID is required."
        )

    if not employee_id:
        raise LeaveApprovalException(
            "Employee ID is required."
        )


def apply_leave(
    employee_id,
    leave_type,
    start_date,
    end_date,
    reason
):

    try:

        validate_leave_request(
            employee_id,
            leave_type,
            start_date,
            end_date,
            reason
        )


        existing_leaves = get_employee_leave_requests(
            employee_id
        )


        for leave in existing_leaves:

            if leave["status"] in ["Pending", "Approved"]:

                existing_start = leave["start_date"]
                existing_end = leave["end_date"]


                if (
                    start_date <= existing_end
                    and end_date >= existing_start
                ):

                    raise LeaveOverlapException(
                        "You already have a pending or approved leave request in this date range."
                    )


        create_leave_request(
            employee_id=employee_id,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=reason
        )


        logger.info(
            "Leave applied successfully: employee_id=%s type=%s start=%s end=%s",
            employee_id,
            leave_type,
            start_date,
            end_date
        )


        log_action(
            performed_by=employee_id,
            target_employee_id=employee_id,
            action="Leave Applied",
            description=(
                f"Employee applied for {leave_type} "
                f"leave from {start_date} to {end_date}."
            )
        )


        return True, "Leave request submitted successfully."


    except InvalidLeaveRequest as e:

        logger.warning(
            "Invalid leave request: employee_id=%s error=%s",
            employee_id,
            str(e)
        )

        return False, str(e)


    except LeaveOverlapException as e:

        logger.warning(
            "Leave overlap detected: employee_id=%s start=%s end=%s",
            employee_id,
            start_date,
            end_date
        )

        return False, str(e)


    except Exception as e:

        logger.error(
            "Unexpected leave application error: employee_id=%s error=%s",
            employee_id,
            str(e),
            exc_info=True
        )

        return False, "Unable to submit leave request. Please try again."


def get_my_leave_history(employee_id):

    return get_employee_leave_requests(
        employee_id
    )


def get_leave_requests_for_admin():

    return get_all_leave_requests()


def approve_leave(
    leave_id,
    admin_id,
    employee_id,
    admin_comment=None
):

    conn = None

    try:

        validate_leave_action(
            leave_id,
            admin_id,
            employee_id
        )


        conn = get_transaction_connection()

        conn.start_transaction()


        update_leave_status(
            leave_id=leave_id,
            status="Approved",
            reviewed_by=admin_id,
            admin_comment=admin_comment,
            conn=conn
        )


        log_action(
            performed_by=admin_id,
            target_employee_id=employee_id,
            action="Leave Approved",
            description=f"Leave request {leave_id} approved.",
            conn=conn
        )


        conn.commit()


        logger.info(
            "Leave approved successfully: leave_id=%s admin_id=%s",
            leave_id,
            admin_id
        )


        return True, "Leave approved successfully."


    except LeaveApprovalException as e:

        logger.warning(
            "Invalid leave approval request: %s",
            str(e)
        )

        return False, str(e)


    except Exception as e:

        if conn:
            conn.rollback()


        logger.error(
            "Leave approval failed: leave_id=%s admin_id=%s error=%s",
            leave_id,
            admin_id,
            str(e),
            exc_info=True
        )


        return False, "Unable to approve leave request. Please try again."


    finally:

        if conn:
            conn.close()



def reject_leave(
    leave_id,
    admin_id,
    employee_id,
    admin_comment=None
):

    conn = None

    try:

        validate_leave_action(
            leave_id,
            admin_id,
            employee_id
        )


        conn = get_transaction_connection()

        conn.start_transaction()


        update_leave_status(
            leave_id=leave_id,
            status="Rejected",
            reviewed_by=admin_id,
            admin_comment=admin_comment,
            conn=conn
        )


        log_action(
            performed_by=admin_id,
            target_employee_id=employee_id,
            action="Leave Rejected",
            description=f"Leave request {leave_id} rejected.",
            conn=conn
        )


        conn.commit()


        logger.info(
            "Leave rejected successfully: leave_id=%s admin_id=%s",
            leave_id,
            admin_id
        )


        return True, "Leave rejected successfully."


    except LeaveApprovalException as e:

        logger.warning(
            "Invalid leave rejection request: %s",
            str(e)
        )

        return False, str(e)


    except Exception as e:

        if conn:
            conn.rollback()


        logger.error(
            "Leave rejection failed: leave_id=%s admin_id=%s error=%s",
            leave_id,
            admin_id,
            str(e),
            exc_info=True
        )


        return False, "Unable to reject leave request. Please try again."


    finally:

        if conn:
            conn.close()



def get_leave_kpis():

    return get_leave_summary()



def get_my_leave_kpis(employee_id):

    return get_employee_leave_summary(
        employee_id
    )



def is_employee_on_leave(
    employee_id,
    target_date
):

    leave = get_approved_leave_for_date(
        employee_id,
        target_date
    )

    return leave is not None