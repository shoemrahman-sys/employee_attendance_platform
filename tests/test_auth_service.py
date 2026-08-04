from unittest.mock import patch
from datetime import datetime, timedelta

from services.auth_service import (
    register_user,
    login_user,
    admin_reset_password
)


def test_register_user_success():

    with patch(
        "services.auth_service.get_employee_by_email",
        return_value=None
    ), patch(
        "services.auth_service.create_employee"
    ):

        result, message = register_user(
            full_name="John Doe",
            email="john@test.com",
            phone="9999999999",
            dept_id=1,
            shift_id=1,
            job_title="Developer",
            password="Password@123"
        )


    assert result is True
    assert "successful" in message



def test_register_existing_email():

    with patch(
        "services.auth_service.get_employee_by_email",
        return_value={
            "employee_id":101
        }
    ):

        result, message = register_user(
            full_name="John Doe",
            email="john@test.com",
            phone="9999999999",
            dept_id=1,
            shift_id=1,
            job_title="Developer",
            password="Password@123"
        )


    assert result is False
    assert "already registered" in message



def test_register_invalid_email():

    result, message = register_user(
        full_name="John Doe",
        email="wrong-email",
        phone="9999999999",
        dept_id=1,
        shift_id=1,
        job_title="Developer",
        password="Password@123"
    )


    assert result is False
    assert "Invalid email" in message



def test_register_invalid_password():

    result, message = register_user(
        full_name="John Doe",
        email="john@test.com",
        phone="9999999999",
        dept_id=1,
        shift_id=1,
        job_title="Developer",
        password="123"
    )


    assert result is False
    assert message == "Invalid password format."



def test_login_success():

    employee = {
        "employee_id":101,
        "password_hash":"hashed_password"
    }


    with patch(
        "services.auth_service.get_employee_by_email",
        return_value=employee
    ), patch(
        "services.auth_service.verify_password",
        return_value=True
    ), patch(
        "services.auth_service.reset_login_attempts"
    ):

        result, response = login_user(
            "john@test.com",
            "Password@123"
        )


    assert result is True
    assert response == employee



def test_login_wrong_password():

    employee = {
        "employee_id":101,
        "password_hash":"hashed_password"
    }


    with patch(
        "services.auth_service.get_employee_by_email",
        return_value=employee
    ), patch(
        "services.auth_service.verify_password",
        return_value=False
    ), patch(
        "services.auth_service.record_failed_attempt"
    ):

        result, message = login_user(
            "john@test.com",
            "wrongpassword"
        )


    assert result is False
    assert "Invalid email or password" in message



def test_login_locked_account():

    locked_time = datetime.now() + timedelta(minutes=10)

    attempt = {
        "locked_until": locked_time
    }


    with patch(
        "services.auth_service.get_login_attempt",
        return_value=attempt
    ):

        result, message = login_user(
            "john@test.com",
            "Password@123"
        )


    assert result is False
    assert "Too many failed login attempts" in message



def test_admin_reset_password_success():

    with patch(
        "services.auth_service.update_password"
    ):

        result, message = admin_reset_password(
            employee_id=101,
            new_password="NewPassword@123"
        )


    assert result is True
    assert "successfully" in message