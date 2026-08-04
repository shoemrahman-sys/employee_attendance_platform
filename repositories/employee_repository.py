from config.database import read_cursor, write_cursor

def create_employee(
    full_name,
    email,
    phone,
    dept_id,
    shift_id,
    job_title,
    password_hash,
    role="employee"
):
    with write_cursor() as cursor:
        cursor.execute("""
            INSERT INTO employees
            (full_name, email, phone, dept_id, shift_id,
             job_title, password_hash, role)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            full_name,
            email,
            phone,
            dept_id,
            shift_id,
            job_title,
            password_hash,
            role
        ))
def get_employee_by_email(email):
    with read_cursor(dictionary=True) as cursor:
        cursor.execute("""
            SELECT
                e.employee_id,
                e.full_name,
                e.email,
                e.phone,
                e.dept_id,
                e.shift_id,
                e.job_title,
                e.password_hash,
                e.role,
                d.dept_name,
                s.shift_name
            FROM employees e
            LEFT JOIN departments d
                ON e.dept_id = d.dept_id
            LEFT JOIN shifts s
                ON e.shift_id = s.shift_id
            WHERE e.email = %s
              AND e.is_active = TRUE
        """, (email,))

        return cursor.fetchone()

def get_all_employees():
    with read_cursor(dictionary=True) as cursor:
        cursor.execute("""
            SELECT
                e.employee_id,
                e.full_name,
                e.email,
                e.phone,
                e.job_title,
                e.role,
                e.is_active,
                d.dept_name,
                s.shift_name,
                e.created_at
            FROM employees e
            LEFT JOIN departments d
                ON e.dept_id = d.dept_id
            LEFT JOIN shifts s
                ON e.shift_id = s.shift_id
            ORDER BY e.employee_id DESC
        """)

        return cursor.fetchall()

def update_password(employee_id, password_hash):
    with write_cursor() as cursor:
        cursor.execute("""
            UPDATE employees
            SET password_hash = %s
            WHERE employee_id = %s
        """, (password_hash, employee_id))

def deactivate_employee(employee_id):
    with write_cursor() as cursor:
        cursor.execute("""
            UPDATE employees
            SET is_active = FALSE
            WHERE employee_id = %s
        """, (employee_id,))

def activate_employee(employee_id):
    with write_cursor() as cursor:
        cursor.execute("""
            UPDATE employees
            SET is_active = TRUE
            WHERE employee_id = %s
        """, (employee_id,))