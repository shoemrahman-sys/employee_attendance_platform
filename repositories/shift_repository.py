from config.database import read_cursor

def get_active_shifts():
    with read_cursor(dictionary=True) as cursor:
        cursor.execute("""
            SELECT
                shift_id,
                shift_name,
                start_time,
                end_time,
                expected_hours,
                late_grace_minutes
            FROM shifts
            WHERE is_active = TRUE
            ORDER BY shift_name
        """)

        return cursor.fetchall()

def get_shift_by_employee(employee_id):
    with read_cursor(dictionary=True) as cursor:
        cursor.execute("""
            SELECT
                s.*
            FROM employees e
            JOIN shifts s
                ON e.shift_id = s.shift_id
            WHERE e.employee_id = %s
        """, (employee_id,))

        return cursor.fetchone()