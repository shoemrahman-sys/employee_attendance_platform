from datetime import date, timedelta

from services.leave_service import (
    apply_leave,
    approve_leave,
    reject_leave,
    get_my_leave_history,
    get_leave_requests_for_admin,
    get_leave_kpis,
    get_my_leave_kpis,
    is_employee_on_leave
)


# ==========================================================
# APPLY LEAVE
# ==========================================================

def test_apply_leave_success(sample_leave_dates):

    start_date, end_date = sample_leave_dates

    with patch(
        "services.leave_service.get_employee_leave_requests",
        return_value=[]
    ), patch(
        "services.leave_service.create_leave_request"
    ) as mock_create, patch(
        "services.leave_service.log_action"
    ):

        result, message = apply_leave(
            employee_id=101,
            leave_type="Casual Leave",
            start_date=start_date,
            end_date=end_date,
            reason="Family Function"
        )

    assert result is True
    assert message == "Leave request submitted successfully."
    mock_create.assert_called_once()


def test_apply_leave_missing_employee(sample_leave_dates):

    start_date, end_date = sample_leave_dates

    result, message = apply_leave(
        employee_id=None,
        leave_type="Casual Leave",
        start_date=start_date,
        end_date=end_date,
        reason="Reason"
    )

    assert result is False
    assert "Employee ID" in message


def test_apply_leave_missing_leave_type(sample_leave_dates):

    start_date, end_date = sample_leave_dates

    result, message = apply_leave(
        employee_id=101,
        leave_type="",
        start_date=start_date,
        end_date=end_date,
        reason="Reason"
    )

    assert result is False


def test_apply_leave_start_after_end():

    start = date.today() + timedelta(days=5)
    end = date.today() + timedelta(days=2)

    result, message = apply_leave(
        101,
        "Casual Leave",
        start,
        end,
        "Reason"
    )

    assert result is False
    assert "after" in message.lower()


def test_apply_leave_past_date():

    start = date.today() - timedelta(days=1)
    end = date.today()

    result, message = apply_leave(
        101,
        "Casual Leave",
        start,
        end,
        "Reason"
    )

    assert result is False
    assert "past" in message.lower()


def test_apply_leave_missing_reason(sample_leave_dates):

    start_date, end_date = sample_leave_dates

    result, message = apply_leave(
        101,
        "Casual Leave",
        start_date,
        end_date,
        ""
    )

    assert result is False
    assert "reason" in message.lower()


def test_apply_leave_duration_limit():

    start = date.today() + timedelta(days=5)
    end = start + timedelta(days=20)

    result, message = apply_leave(
        101,
        "Casual Leave",
        start,
        end,
        "Vacation"
    )

    assert result is False
    assert "15" in message


def test_apply_leave_overlap(sample_leave_dates):

    start_date, end_date = sample_leave_dates

    existing_leave = [{
        "status": "Approved",
        "start_date": start_date,
        "end_date": end_date
    }]

    with patch(
        "services.leave_service.get_employee_leave_requests",
        return_value=existing_leave
    ):

        result, message = apply_leave(
            101,
            "Casual Leave",
            start_date,
            end_date,
            "Vacation"
        )

    assert result is False
    assert "already have" in message.lower()


def test_apply_leave_repository_failure(sample_leave_dates):

    start_date, end_date = sample_leave_dates

    with patch(
        "services.leave_service.get_employee_leave_requests",
        return_value=[]
    ), patch(
        "services.leave_service.create_leave_request",
        side_effect=Exception("Database Error")
    ):

        result, message = apply_leave(
            101,
            "Casual Leave",
            start_date,
            end_date,
            "Vacation"
        )

    assert result is False


# ==========================================================
# READ OPERATIONS
# ==========================================================

def test_get_my_leave_history():

    expected = [{"leave_id": 1}]

    with patch(
        "services.leave_service.get_employee_leave_requests",
        return_value=expected
    ):

        result = get_my_leave_history(101)

    assert result == expected


def test_get_leave_requests_for_admin():

    expected = [{"leave_id": 1}]

    with patch(
        "services.leave_service.get_all_leave_requests",
        return_value=expected
    ):

        result = get_leave_requests_for_admin()

    assert result == expected


def test_get_leave_kpis():

    expected = {
        "approved": 5
    }

    with patch(
        "services.leave_service.get_leave_summary",
        return_value=expected
    ):

        result = get_leave_kpis()

    assert result == expected


def test_get_my_leave_kpis():

    expected = {
        "approved": 2
    }

    with patch(
        "services.leave_service.get_employee_leave_summary",
        return_value=expected
    ):

        result = get_my_leave_kpis(101)

    assert result == expected


def test_employee_on_leave_true():

    with patch(
        "services.leave_service.get_approved_leave_for_date",
        return_value={"leave_id": 1}
    ):

        assert is_employee_on_leave(
            101,
            date.today()
        ) is True


def test_employee_on_leave_false():

    with patch(
        "services.leave_service.get_approved_leave_for_date",
        return_value=None
    ):

        assert is_employee_on_leave(
            101,
            date.today()
        ) is False

from unittest.mock import Mock, patch


# ==========================================================
# APPROVE LEAVE
# ==========================================================

def test_approve_leave_success():

    mock_conn = Mock()

    with patch(
        "services.leave_service.get_transaction_connection",
        return_value=mock_conn
    ), patch(
        "services.leave_service.update_leave_status"
    ) as mock_update, patch(
        "services.leave_service.log_action"
    ) as mock_log:

        result, message = approve_leave(
            leave_id=1,
            admin_id=10,
            employee_id=101,
            admin_comment="Approved"
        )

    assert result is True
    assert message == "Leave approved successfully."

    mock_conn.start_transaction.assert_called_once()
    mock_update.assert_called_once()
    mock_log.assert_called_once()
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()


def test_approve_leave_repository_exception():

    mock_conn = Mock()

    with patch(
        "services.leave_service.get_transaction_connection",
        return_value=mock_conn
    ), patch(
        "services.leave_service.update_leave_status",
        side_effect=Exception("Database Error")
    ):

        result, message = approve_leave(
            leave_id=1,
            admin_id=10,
            employee_id=101
        )

    assert result is False
    assert "Unable to approve" in message

    mock_conn.rollback.assert_called_once()
    mock_conn.close.assert_called_once()


def test_approve_leave_log_failure():

    mock_conn = Mock()

    with patch(
        "services.leave_service.get_transaction_connection",
        return_value=mock_conn
    ), patch(
        "services.leave_service.update_leave_status"
    ), patch(
        "services.leave_service.log_action",
        side_effect=Exception("Audit Failed")
    ):

        result, message = approve_leave(
            leave_id=1,
            admin_id=10,
            employee_id=101
        )

    assert result is False

    mock_conn.rollback.assert_called_once()
    mock_conn.close.assert_called_once()


# ==========================================================
# REJECT LEAVE
# ==========================================================

def test_reject_leave_success():

    mock_conn = Mock()

    with patch(
        "services.leave_service.get_transaction_connection",
        return_value=mock_conn
    ), patch(
        "services.leave_service.update_leave_status"
    ) as mock_update, patch(
        "services.leave_service.log_action"
    ) as mock_log:

        result, message = reject_leave(
            leave_id=1,
            admin_id=10,
            employee_id=101,
            admin_comment="Rejected"
        )

    assert result is True
    assert message == "Leave rejected successfully."

    mock_conn.start_transaction.assert_called_once()
    mock_update.assert_called_once()
    mock_log.assert_called_once()
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()


def test_reject_leave_repository_exception():

    mock_conn = Mock()

    with patch(
        "services.leave_service.get_transaction_connection",
        return_value=mock_conn
    ), patch(
        "services.leave_service.update_leave_status",
        side_effect=Exception("Database Error")
    ):

        result, message = reject_leave(
            leave_id=1,
            admin_id=10,
            employee_id=101
        )

    assert result is False
    assert "Unable to reject" in message

    mock_conn.rollback.assert_called_once()
    mock_conn.close.assert_called_once()


def test_reject_leave_log_failure():

    mock_conn = Mock()

    with patch(
        "services.leave_service.get_transaction_connection",
        return_value=mock_conn
    ), patch(
        "services.leave_service.update_leave_status"
    ), patch(
        "services.leave_service.log_action",
        side_effect=Exception("Audit Failed")
    ):

        result, message = reject_leave(
            leave_id=1,
            admin_id=10,
            employee_id=101
        )

    assert result is False

    mock_conn.rollback.assert_called_once()
    mock_conn.close.assert_called_once()