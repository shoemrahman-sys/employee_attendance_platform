from repositories.employee_repository import create_employee, get_employee_by_email
from utils.password_utils import hash_password, verify_password
from utils.validators import is_valid_email, is_valid_password, is_not_empty
from repositories.employee_repository import get_employee_by_email, update_password

def register_user(full_name, email, phone, dept_id, shift_id, job_title, password):
    if not is_not_empty(full_name):
        return False, "Full name is required."

    if not is_valid_email(email):
        return False, "Invalid email address."

    if not is_valid_password(password):
        return False, "Password must be at least 6 characters."

    existing_user = get_employee_by_email(email)
    if existing_user:
        return False, "Email already registered."

    password_hash = hash_password(password)

    try:
        create_employee(
            full_name=full_name,
            email=email,
            phone=phone,
            dept_id=dept_id,
            shift_id=shift_id,
            job_title=job_title,
            password_hash=password_hash
        )
        return True, "Registration successful. Please login."
    except Exception as e:
        return False, f"Registration failed: {e}"

def login_user(email, password):
    employee = get_employee_by_email(email)

    if not employee:
        return None

    if verify_password(password, employee["password_hash"]):
        return employee

    return None

def admin_reset_password(employee_id, new_password):
    if len(new_password) < 6:
        return False, "Password must be at least 6 characters."

    password_hash = hash_password(new_password)

    update_password(
        employee_id=employee_id,
        password_hash=password_hash
    )

    return True, "Password reset successfully."