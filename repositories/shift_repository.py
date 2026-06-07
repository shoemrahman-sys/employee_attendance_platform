from config.database import get_db_connection

def get_active_shifts():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT shift_id, shift_name, start_time, end_time, expected_hours, late_grace_minutes
        FROM shifts
        WHERE is_active = TRUE
        ORDER BY shift_name
    """)

    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def get_shift_by_employee(employee_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.*
        FROM employees e
        JOIN shifts s ON e.shift_id = s.shift_id
        WHERE e.employee_id = %s
    """, (employee_id,))

    shift = cursor.fetchone()
    cursor.close()
    conn.close()
    return shift