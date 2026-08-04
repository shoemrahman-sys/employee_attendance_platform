from unittest.mock import patch

from services.audit_service import log_action



def test_log_action_success():

    with patch(
        "services.audit_service.create_audit_log"
    ) as mock_create_log:


        log_action(
            performed_by=101,
            target_employee_id=101,
            action="Leave Applied",
            description="Employee applied for leave."
        )


    mock_create_log.assert_called_once_with(
        performed_by=101,
        target_employee_id=101,
        action="Leave Applied",
        description="Employee applied for leave.",
        conn=None
    )



def test_log_action_with_transaction_connection():

    mock_connection = object()


    with patch(
        "services.audit_service.create_audit_log"
    ) as mock_create_log:


        log_action(
            performed_by=5,
            target_employee_id=101,
            action="Leave Approved",
            description="Admin approved leave.",
            conn=mock_connection
        )


    mock_create_log.assert_called_once_with(
        performed_by=5,
        target_employee_id=101,
        action="Leave Approved",
        description="Admin approved leave.",
        conn=mock_connection
    )



def test_log_action_invalid_action():

    with patch(
        "services.audit_service.create_audit_log"
    ) as mock_create_log:

        result = log_action()

    assert result is False
    mock_create_log.assert_not_called()