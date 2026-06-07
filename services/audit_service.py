from repositories.audit_repository import create_audit_log


def log_action(
    performed_by=None,
    target_employee_id=None,
    action="",
    description=""
):
    create_audit_log(
        performed_by=performed_by,
        target_employee_id=target_employee_id,
        action=action,
        description=description
    )