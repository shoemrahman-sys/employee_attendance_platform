from unittest.mock import patch
from datetime import datetime, date, time
from exceptions.attendance_exceptions import InvalidAttendanceRequest

import pytest


from services.attendance_service import (
    check_in_employee,
    check_out_employee,
    calculate_status,
    calculate_late_details,
    convert_mysql_time
)



def test_check_in_success():

    shift = {
        "start_time": time(9,0),
        "late_grace_minutes": 10
    }


    with patch(
        "services.attendance_service.get_today_attendance",
        return_value=None
    ), patch(
        "services.attendance_service.get_shift_by_employee",
        return_value=shift
    ), patch(
        "services.attendance_service.create_check_in"
    ):

        result, message = check_in_employee(
            employee_id=101
        )


    assert result is True
    assert message == "Check-in successful."



def test_duplicate_check_in():

    with patch(
        "services.attendance_service.get_today_attendance",
        return_value={
            "attendance_id":1
        }
    ):

        result, message = check_in_employee(
            employee_id=101
        )


    assert result is False
    assert "already checked in" in message



def test_check_in_without_employee():

    result, message = check_in_employee(
        employee_id=None
    )


    assert result is False
    assert "Employee ID" in message



def test_check_in_without_shift():

    with patch(
        "services.attendance_service.get_today_attendance",
        return_value=None
    ), patch(
        "services.attendance_service.get_shift_by_employee",
        return_value=None
    ):

        result, message = check_in_employee(
            employee_id=101
        )


    assert result is False
    assert "shift" in message

def test_check_in_unexpected_exception():

    with patch(
        "services.attendance_service.get_today_attendance",
        side_effect=Exception("Database Error")
    ):

        result, message = check_in_employee(
            employee_id=101
        )

    assert result is False
    assert "Unable to complete check-in" in message


def test_checkout_success():

    attendance = {
        "attendance_id":1,
        "check_in": datetime.now(),
        "check_out":None
    }


    shift = {
        "expected_hours":8
    }


    with patch(
        "services.attendance_service.get_today_attendance",
        return_value=attendance
    ), patch(
        "services.attendance_service.get_shift_by_employee",
        return_value=shift
    ), patch(
        "services.attendance_service.update_check_out"
    ):

        result, message = check_out_employee(
            employee_id=101
        )


    assert result is True
    assert "Check-out successful" in message



def test_checkout_without_checkin():

    with patch(
        "services.attendance_service.get_today_attendance",
        return_value=None
    ):

        result, message = check_out_employee(
            employee_id=101
        )


    assert result is False
    assert "check out before check-in" in message



def test_duplicate_checkout():

    with patch(
        "services.attendance_service.get_today_attendance",
        return_value={
            "attendance_id":1,
            "check_out":datetime.now()
        }
    ):

        result, message = check_out_employee(
            employee_id=101
        )


    assert result is False
    assert "already checked out" in message

def test_checkout_without_shift():

    attendance = {
        "attendance_id": 1,
        "check_in": datetime.now(),
        "check_out": None
    }

    with patch(
        "services.attendance_service.get_today_attendance",
        return_value=attendance
    ), patch(
        "services.attendance_service.get_shift_by_employee",
        return_value=None
    ):

        result, message = check_out_employee(
            employee_id=101
        )

    assert result is False
    assert "shift" in message.lower()

def test_checkout_unexpected_exception():

    with patch(
        "services.attendance_service.get_today_attendance",
        side_effect=Exception("Database Error")
    ):

        result, message = check_out_employee(
            employee_id=101
        )

    assert result is False
    assert "Unable to complete checkout" in message

def test_calculate_status():

    assert calculate_status(8,8) == "Present"

    assert calculate_status(5,8) == "Half Day"

    assert calculate_status(2,8) == "Absent"



def test_late_calculation():

    shift = {
        "start_time":time(9,0),
        "late_grace_minutes":10
    }


    late_time = datetime.combine(
        date.today(),
        time(9,30)
    )


    is_late, minutes = calculate_late_details(
        late_time,
        shift
    )


    assert is_late is True
    assert minutes == 20

def test_late_calculation_not_late():

    shift = {
        "start_time": time(9, 0),
        "late_grace_minutes": 10
    }

    check_in = datetime.combine(
        date.today(),
        time(9, 5)
    )

    is_late, minutes = calculate_late_details(
        check_in,
        shift
    )

    assert is_late is False
    assert minutes == 0

def test_convert_mysql_time_invalid_type():

    with pytest.raises(InvalidAttendanceRequest):
        convert_mysql_time("09:00")