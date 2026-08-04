from datetime import datetime, date, timedelta, time

from utils.logger import logger

from repositories.attendance_repository import (
    get_today_attendance,
    create_check_in,
    update_check_out
)

from repositories.shift_repository import (
    get_shift_by_employee
)

from exceptions.attendance_exceptions import (
    InvalidAttendanceRequest,
    ShiftNotAssignedException,
    AttendanceAlreadyExists
)


def convert_mysql_time(value):

    if isinstance(value, time):
        return value

    if isinstance(value, timedelta):

        total_seconds = int(
            value.total_seconds()
        )

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        return time(
            hour=hours % 24,
            minute=minutes,
            second=seconds
        )

    logger.error(
        "Unsupported time format received: %s",
        type(value)
    )

    raise InvalidAttendanceRequest(
        "Invalid shift time format."
    )



def validate_employee(employee_id):

    if not employee_id:
        raise InvalidAttendanceRequest(
            "Employee ID is required."
        )



def get_employee_shift(employee_id):

    shift = get_shift_by_employee(
        employee_id
    )

    if not shift:
        raise ShiftNotAssignedException(
            "No shift assigned to this employee."
        )

    return shift



def calculate_late_details(
    check_in_time,
    shift
):

    shift_start_time = convert_mysql_time(
        shift["start_time"]
    )


    shift_start = datetime.combine(
        date.today(),
        shift_start_time
    )


    grace_time = shift_start + timedelta(
        minutes=int(
            shift["late_grace_minutes"]
        )
    )


    if check_in_time > grace_time:

        late_minutes = int(
            (
                check_in_time - grace_time
            ).total_seconds() / 60
        )

        return True, late_minutes


    return False, 0



def calculate_status(
    working_hours,
    expected_hours
):

    if working_hours >= expected_hours:
        return "Present"

    elif working_hours >= expected_hours / 2:
        return "Half Day"

    else:
        return "Absent"



def check_in_employee(
    employee_id
):

    try:

        validate_employee(
            employee_id
        )


        today_record = get_today_attendance(
            employee_id
        )


        if today_record:

            raise AttendanceAlreadyExists(
                "You have already checked in today."
            )


        shift = get_employee_shift(
            employee_id
        )


        now = datetime.now()


        is_late, late_minutes = calculate_late_details(
            now,
            shift
        )


        create_check_in(
            employee_id=employee_id,
            work_date=date.today(),
            check_in=now,
            is_late=is_late,
            late_minutes=late_minutes
        )


        logger.info(
            "Employee checked in successfully: employee_id=%s late=%s minutes=%s",
            employee_id,
            is_late,
            late_minutes
        )


        return True, "Check-in successful."



    except InvalidAttendanceRequest as e:

        logger.warning(
            "Invalid check-in request: employee_id=%s error=%s",
            employee_id,
            str(e)
        )

        return False, str(e)



    except AttendanceAlreadyExists as e:

        logger.warning(
            "Duplicate check-in attempt: employee_id=%s",
            employee_id
        )

        return False, str(e)



    except ShiftNotAssignedException as e:

        logger.warning(
            "No shift assigned: employee_id=%s",
            employee_id
        )

        return False, str(e)



    except Exception as e:

        logger.error(
            "Check-in failed: employee_id=%s error=%s",
            employee_id,
            str(e),
            exc_info=True
        )

        return False, "Unable to complete check-in. Please try again."



def check_out_employee(
    employee_id
):

    try:

        validate_employee(
            employee_id
        )


        attendance = get_today_attendance(
            employee_id
        )


        if not attendance:

            raise InvalidAttendanceRequest(
                "You cannot check out before check-in."
            )


        if attendance["check_out"] is not None:

            raise AttendanceAlreadyExists(
                "You have already checked out today."
            )


        shift = get_employee_shift(
            employee_id
        )


        now = datetime.now()


        check_in_time = attendance["check_in"]


        total_seconds = (
            now - check_in_time
        ).total_seconds()


        working_hours = round(
            total_seconds / 3600,
            2
        )


        expected_hours = float(
            shift["expected_hours"]
        )


        overtime_hours = round(
            max(
                0,
                working_hours - expected_hours
            ),
            2
        )


        status = calculate_status(
            working_hours,
            expected_hours
        )


        update_check_out(
            attendance_id=attendance["attendance_id"],
            check_out=now,
            working_hours=working_hours,
            overtime_hours=overtime_hours,
            status=status
        )


        logger.info(
            "Employee checked out successfully: employee_id=%s working_hours=%s status=%s",
            employee_id,
            working_hours,
            status
        )


        return True, (
            f"Check-out successful. "
            f"Working Hours: {working_hours}"
        )



    except InvalidAttendanceRequest as e:

        logger.warning(
            "Invalid checkout request: employee_id=%s error=%s",
            employee_id,
            str(e)
        )

        return False, str(e)



    except AttendanceAlreadyExists as e:

        logger.warning(
            "Duplicate checkout attempt: employee_id=%s",
            employee_id
        )

        return False, str(e)



    except ShiftNotAssignedException as e:

        logger.warning(
            "No shift assigned: employee_id=%s",
            employee_id
        )

        return False, str(e)



    except Exception as e:

        logger.error(
            "Checkout failed: employee_id=%s error=%s",
            employee_id,
            str(e),
            exc_info=True
        )

        return False, "Unable to complete checkout. Please try again."