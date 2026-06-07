import re

def is_valid_email(email: str) -> bool:
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None

def is_valid_password(password: str) -> bool:
    return len(password) >= 6

def is_not_empty(value: str) -> bool:
    return value is not None and value.strip() != ""