import re

def is_valid_email(email: str) -> bool:
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None

def is_valid_password(password: str) -> bool:
    """
    Password must:
    - Be at least 8 characters
    - Contain one uppercase letter
    - Contain one lowercase letter
    - Contain one digit
    - Contain one special character
    """

    if len(password) < 8:
        return False

    if not re.search(r"[A-Z]", password):
        return False

    if not re.search(r"[a-z]", password):
        return False

    if not re.search(r"\d", password):
        return False

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=/\\[\]]", password):
        return False

    return True


def is_not_empty(value: str) -> bool:
    return value is not None and value.strip() != ""

