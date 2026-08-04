from datetime import datetime

from utils.logger import logger

from repositories.employee_repository import (
    create_employee,
    get_employee_by_email,
    update_password
)

from utils.password_utils import (
    hash_password,
    verify_password
)

from utils.validators import (
    is_valid_email,
    is_valid_password,
    is_not_empty
)

from repositories.login_attempt_repository import (
    create_login_attempt,
    get_login_attempt,
    record_failed_attempt,
    reset_login_attempts
)

from exceptions.auth_exceptions import (
    InvalidRegistration,
    InvalidLogin,
    AccountLocked,
    PasswordResetException
)



def validate_registration(
    full_name,
    email,
    password
):

    if not is_not_empty(full_name):
        raise InvalidRegistration(
            "Full name is required."
        )


    if not is_valid_email(email):
        raise InvalidRegistration(
            "Invalid email address."
        )


    if not is_valid_password(password):
        raise InvalidRegistration(
            "Invalid password format."
        )



def validate_login(
    email,
    password
):

    if not is_valid_email(email):
        raise InvalidLogin(
            "Invalid email or password."
        )


    if not password:
        raise InvalidLogin(
            "Invalid email or password."
        )



def register_user(
    full_name,
    email,
    phone,
    dept_id,
    shift_id,
    job_title,
    password
):

    try:

        validate_registration(
            full_name,
            email,
            password
        )


        existing_user = get_employee_by_email(
            email
        )


        if existing_user:

            logger.warning(
                "Registration attempted with existing account"
            )

            return False, "Email already registered."


        password_hash = hash_password(
            password
        )


        create_employee(
            full_name=full_name,
            email=email,
            phone=phone,
            dept_id=dept_id,
            shift_id=shift_id,
            job_title=job_title,
            password_hash=password_hash
        )


        logger.info(
            "New employee registered successfully"
        )


        return True, (
            "Registration successful. "
            "Please login."
        )


    except InvalidRegistration as e:

        logger.warning(
            "Invalid registration attempt: %s",
            str(e)
        )

        return False, str(e)


    except Exception as e:

        logger.error(
            "Registration failed: %s",
            str(e),
            exc_info=True
        )

        return False, (
            "Registration failed. "
            "Please try again."
        )



def login_user(
    email,
    password
):

    try:

        validate_login(
            email,
            password
        )


        create_login_attempt(
            email
        )


        attempt = get_login_attempt(
            email
        )


        if (
            attempt
            and attempt["locked_until"] is not None
            and attempt["locked_until"] > datetime.now()
        ):

            remaining = (
                attempt["locked_until"]
                - datetime.now()
            )


            minutes = int(
                remaining.total_seconds() // 60
            ) + 1


            logger.warning(
                "Login blocked due to account lock"
            )


            raise AccountLocked(
                f"Too many failed login attempts. "
                f"Please try again in {minutes} minute(s)."
            )


        employee = get_employee_by_email(
            email
        )


        if (
            not employee
            or not verify_password(
                password,
                employee["password_hash"]
            )
        ):

            record_failed_attempt(
                email
            )


            logger.warning(
                "Failed login attempt"
            )


            raise InvalidLogin(
                "Invalid email or password."
            )


        reset_login_attempts(
            email
        )


        logger.info(
            "Successful login: employee_id=%s",
            employee["employee_id"]
        )


        return True, employee



    except AccountLocked as e:

        return False, str(e)



    except InvalidLogin as e:

        return False, str(e)



    except Exception as e:

        logger.error(
            "Login failed: %s",
            str(e),
            exc_info=True
        )

        return False, (
            "Unable to login. "
            "Please try again."
        )



def admin_reset_password(
    employee_id,
    new_password
):

    try:

        if not employee_id:

            raise PasswordResetException(
                "Employee ID is required."
            )


        if not is_valid_password(
            new_password
        ):

            raise PasswordResetException(
                "Password does not meet security requirements."
            )


        password_hash = hash_password(
            new_password
        )


        update_password(
            employee_id=employee_id,
            password_hash=password_hash
        )


        logger.info(
            "Password reset successfully: employee_id=%s",
            employee_id
        )


        return True, (
            "Password reset successfully."
        )


    except PasswordResetException as e:

        logger.warning(
            "Password reset validation failed: %s",
            str(e)
        )

        return False, str(e)


    except Exception as e:

        logger.error(
            "Password reset failed: employee_id=%s error=%s",
            employee_id,
            str(e),
            exc_info=True
        )

        return False, (
            "Unable to reset password. "
            "Please try again."
        )