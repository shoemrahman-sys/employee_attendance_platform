from config.database import get_db_connection

def create_employee(full_name, email, phone, dept_id, shift_id, job_title,password_hash, role="employee"):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO employees
        (full_name, email, phone, dept_id, shift_id, job_title,password_hash, role)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (full_name, email, phone, dept_id, shift_id,job_title, password_hash, role))

    conn.commit()
    cursor.close()
    conn.close()

def get_employee_by_email(email):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

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
        LEFT JOIN departments d ON e.dept_id = d.dept_id
        LEFT JOIN shifts s ON e.shift_id = s.shift_id
        WHERE e.email = %s AND e.is_active = TRUE
    """, (email,))

    employee = cursor.fetchone()
    cursor.close()
    conn.close()
    return employee

def get_all_employees():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

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
        LEFT JOIN departments d ON e.dept_id = d.dept_id
        LEFT JOIN shifts s ON e.shift_id = s.shift_id
        ORDER BY e.employee_id DESC
    """)

    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def update_employee_password(email, new_password_hash):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE employees
            SET password_hash = %s
            WHERE email = %s
        """, (new_password_hash, email))

        conn.commit()
        return cursor.rowcount > 0

    except Exception as e:
        conn.rollback()
        print(f"Password update error: {e}")
        return False

    finally:
        cursor.close()
        conn.close()
def deactivate_employee(employee_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE employees
        SET is_active = FALSE
        WHERE employee_id = %s
    """, (employee_id,))

    conn.commit()
    cursor.close()
    conn.close()

def activate_employee(employee_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE employees
        SET is_active = TRUE
        WHERE employee_id = %s
    """, (employee_id,))

    conn.commit()
    cursor.close()
    conn.close()