from utils.logger import logger

from repositories.audit_repository import (
    create_audit_log
)

from exceptions.audit_exceptions import (
    InvalidAuditRequest
)



def validate_audit_request(
    action,
    description
):

    if not action or action.strip() == "":
        raise InvalidAuditRequest(
            "Audit action is required."
        )


    if not description or description.strip() == "":
        raise InvalidAuditRequest(
            "Audit description is required."
        )



def log_action(
    performed_by=None,
    target_employee_id=None,
    action="",
    description="",
    conn=None
):

    try:

        validate_audit_request(
            action,
            description
        )


        create_audit_log(
            performed_by=performed_by,
            target_employee_id=target_employee_id,
            action=action,
            description=description,
            conn=conn
        )


        logger.info(
            "Audit log created: action=%s performed_by=%s",
            action,
            performed_by
        )


        return True


    except InvalidAuditRequest as e:

        logger.warning(
            "Invalid audit request: %s",
            str(e)
        )

        return False


    except Exception as e:

        logger.error(
            "Audit logging failed: action=%s error=%s",
            action,
            str(e),
            exc_info=True
        )

        return False