from config.database import read_cursor

def get_active_departments():
    with read_cursor(dictionary=True) as cursor:
        cursor.execute("""
            SELECT
                dept_id,
                dept_name,
                location
            FROM departments
            WHERE is_active = TRUE
            ORDER BY dept_name
        """)

        return cursor.fetchall()