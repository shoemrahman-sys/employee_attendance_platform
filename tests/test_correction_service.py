from unittest.mock import Mock, patch
from datetime import datetime

from services.correction_service import (
    submit_correction_request,
    get_my_correction_requests,
    get_correction_requests_for_admin,
    approve_correction,
    reject_correction
)


# ==========================================================
# SUBMIT CORRECTION REQUEST
# ==========================================================

def test_submit_correction_success():

    with patch(
        "services.correction_service.create_correction_request"
    ) as mock_create, patch(
        "services.correction_service.log_action"
    ):

        result, message = submit_correction_request(
            employee_id=101,
            attendance_id=1,
            requested_check_in=datetime.now(),
            requested_check_out=None,
            reason="Forgot to check in"
        )

    assert result is True
    assert message == "Attendance correction request submitted successfully."
    mock_create.assert_called_once()


def test_submit_missing_employee():

    result, message = submit_correction_request(
        employee_id=None,
        attendance_id=1,
        requested_check_in=datetime.now(),
        requested_check_out=None,
        reason="Reason"
    )

    assert result is False
    assert "Employee ID" in message


def test_submit_missing_attendance():

    result, message = submit_correction_request(
        employee_id=101,
        attendance_id=None,
        requested_check_in=datetime.now(),
        requested_check_out=None,
        reason="Reason"
    )

    assert result is False
    assert "attendance" in message.lower()


def test_submit_missing_reason():

    result, message = submit_correction_request(
        employee_id=101,
        attendance_id=1,
        requested_check_in=datetime.now(),
        requested_check_out=None,
        reason=""
    )

    assert result is False
    assert "reason" in message.lower()


def test_submit_missing_times():

    result, message = submit_correction_request(
        employee_id=101,
        attendance_id=1,
        requested_check_in=None,
        requested_check_out=None,
        reason="Forgot"
    )

    assert result is False
    assert "check-in" in message.lower()


def test_submit_repository_exception():

    with patch(
        "services.correction_service.create_correction_request",
        side_effect=Exception("DB Error")
    ):

        result, message = submit_correction_request(
            employee_id=101,
            attendance_id=1,
            requested_check_in=datetime.now(),
            requested_check_out=None,
            reason="Forgot"
        )

    assert result is False
    assert "Unable to submit" in message


# ==========================================================
# READ METHODS
# ==========================================================

def test_get_my_correction_requests():

    expected = [{"correction_id": 1}]

    with patch(
        "services.correction_service.get_employee_correction_requests",
        return_value=expected
    ):

        result = get_my_correction_requests(101)

    assert result == expected


def test_get_correction_requests_for_admin():

    expected = [{"correction_id": 1}]

    with patch(
        "services.correction_service.get_all_correction_requests",
        return_value=expected
    ):

        result = get_correction_requests_for_admin()

    assert result == expected


# ==========================================================
# APPROVE
# ==========================================================

def test_approve_correction_success():

    mock_conn = Mock()

    with patch(
        "services.correction_service.get_transaction_connection",
        return_value=mock_conn
    ), patch(
        "services.correction_service.update_attendance_correction"
    ), patch(
        "services.correction_service.update_correction_status"
    ), patch(
        "services.correction_service.log_action"
    ):

        result, message = approve_correction(
            correction_id=1,
            admin_id=10,
            employee_id=101,
            attendance_id=5,
            requested_check_in=datetime.now(),
            requested_check_out=datetime.now(),
            admin_comment="Approved"
        )

    assert result is True
    assert message == "Attendance correction approved successfully."

    mock_conn.start_transaction.assert_called_once()
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()


def test_approve_correction_exception():

    mock_conn = Mock()

    with patch(
        "services.correction_service.get_transaction_connection",
        return_value=mock_conn
    ), patch(
        "services.correction_service.update_attendance_correction",
        side_effect=Exception("DB Error")
    ):

        result, message = approve_correction(
            correction_id=1,
            admin_id=10,
            employee_id=101,
            attendance_id=5,
            requested_check_in=datetime.now(),
            requested_check_out=datetime.now()
        )

    assert result is False
    assert "Unable to approve" in message

    mock_conn.rollback.assert_called_once()
    mock_conn.close.assert_called_once()


# ==========================================================
# REJECT
# ==========================================================

def test_reject_correction_success():

    mock_conn = Mock()

    with patch(
        "services.correction_service.get_transaction_connection",
        return_value=mock_conn
    ), patch(
        "services.correction_service.update_correction_status"
    ), patch(
        "services.correction_service.log_action"
    ):

        result, message = reject_correction(
            correction_id=1,
            admin_id=10,
            employee_id=101,
            admin_comment="Rejected"
        )

    assert result is True
    assert message == "Attendance correction rejected successfully."

    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()


def test_reject_correction_exception():

    mock_conn = Mock()

    with patch(
        "services.correction_service.get_transaction_connection",
        return_value=mock_conn
    ), patch(
        "services.correction_service.update_correction_status",
        side_effect=Exception("DB Error")
    ):

        result, message = reject_correction(
            correction_id=1,
            admin_id=10,
            employee_id=101
        )

    assert result is False
    assert "Unable to reject" in message

    mock_conn.rollback.assert_called_once()
    mock_conn.close.assert_called_once()