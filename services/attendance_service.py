from datetime import datetime, date
from repositories.attendance_repository import (
    get_today_attendance,
    create_check_in,
    update_check_out
)

def check_in_employee(employee_id):
    today = date.today()
    now = datetime.now()

    attendance = get_today_attendance(employee_id, today)

    if attendance:
        return False, "You have already checked in today."

    create_check_in(employee_id, today, now)
    return True, "Check-in successful."


def check_out_employee(employee_id):
    today = date.today()
    now = datetime.now()

    attendance = get_today_attendance(employee_id, today)

    if attendance is None:
        return False, "You cannot check out before checking in."

    if attendance["check_out_time"] is not None:
        return False, "You have already checked out today."

    check_in_time = attendance["check_in_time"]
    total_seconds = (now - check_in_time).total_seconds()
    working_hours = round(total_seconds / 3600, 2)

    update_check_out(
        attendance["attendance_id"],
        now,
        working_hours
    )

    return True, f"Check-out successful. Working hours: {working_hours}"