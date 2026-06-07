from config.database import get_db_connection

def get_active_departments():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT dept_id, dept_name, location
        FROM departments
        WHERE is_active = TRUE
        ORDER BY dept_name
    """)

    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data