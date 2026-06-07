from repositories.employee_repository import create_employee, get_employee_by_email
from utils.password_utils import hash_password, verify_password
from utils.validators import is_valid_email, is_valid_password, is_not_empty
from repositories.employee_repository import get_employee_by_email, update_employee_password

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
def reset_password(email, new_password, confirm_password):
    if not email:
        return False, "Email is required."

    if not new_password or not confirm_password:
        return False, "Both password fields are required."

    if new_password != confirm_password:
        return False, "Passwords do not match."

    if not is_valid_password(new_password):
        return False, "Password must be at least 6 characters long."

    employee = get_employee_by_email(email)

    if not employee:
        return False, "No account found with this email."

    new_password_hash = hash_password(new_password)

    updated = update_employee_password(email, new_password_hash)

    if updated:
        return True, "Password reset successful. Please login with your new password."

    return False, "Password reset failed. Please try again."