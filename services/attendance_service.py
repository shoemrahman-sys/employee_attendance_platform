from datetime import datetime, date, timedelta,time
from repositories.attendance_repository import (
    get_today_attendance,
    create_check_in,
    update_check_out
)
from repositories.shift_repository import get_shift_by_employee

def convert_mysql_time(value):
    if isinstance(value, time):
        return value

    if isinstance(value, timedelta):
        total_seconds = int(value.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        return time(
            hour=hours % 24,
            minute=minutes,
            second=seconds
        )

    raise TypeError(f"Unsupported time type: {type(value)}")

def calculate_late_details(check_in_time, shift):
    shift_start_time = convert_mysql_time(shift["start_time"])

    shift_start = datetime.combine(
        date.today(),
        shift_start_time
    )

    grace_time = shift_start + timedelta(
        minutes=int(shift["late_grace_minutes"])
    )

    if check_in_time > grace_time:
        late_minutes = int(
            (check_in_time - grace_time).total_seconds() / 60
        )
        return True, late_minutes

    return False, 0

def calculate_status(working_hours, expected_hours):
    if working_hours >= expected_hours:
        return "Present"
    elif working_hours >= expected_hours / 2:
        return "Half Day"
    else:
        return "Absent"

def check_in_employee(employee_id):
    today_record = get_today_attendance(employee_id)

    if today_record:
        return False, "You have already checked in today."

    shift = get_shift_by_employee(employee_id)

    if not shift:
        return False, "No shift assigned to this employee."

    now = datetime.now()
    is_late, late_minutes = calculate_late_details(now, shift)

    create_check_in(
        employee_id=employee_id,
        work_date=date.today(),
        check_in=now,
        is_late=is_late,
        late_minutes=late_minutes
    )

    return True, "Check-in successful."

def check_out_employee(employee_id):
    attendance = get_today_attendance(employee_id)

    if not attendance:
        return False, "You cannot check out before check-in."

    if attendance["check_out"] is not None:
        return False, "You have already checked out today."

    shift = get_shift_by_employee(employee_id)

    if not shift:
        return False, "No shift assigned to this employee."

    now = datetime.now()
    check_in_time = attendance["check_in"]

    total_seconds = (now - check_in_time).total_seconds()
    working_hours = round(total_seconds / 3600, 2)

    expected_hours = float(shift["expected_hours"])
    overtime_hours = round(max(0, working_hours - expected_hours), 2)

    status = calculate_status(working_hours, expected_hours)

    update_check_out(
        attendance_id=attendance["attendance_id"],
        check_out=now,
        working_hours=working_hours,
        overtime_hours=overtime_hours,
        status=status
    )

    return True, f"Check-out successful. Working Hours: {working_hours}"