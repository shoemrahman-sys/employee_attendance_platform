from config.database import get_db_connection


def create_audit_log(
    performed_by=None,
    target_employee_id=None,
    action="",
    description=""
):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO audit_logs (
            performed_by,
            target_employee_id,
            action,
            description
        )
        VALUES (%s, %s, %s, %s)
    """, (
        performed_by,
        target_employee_id,
        action,
        description
    ))

    conn.commit()
    cursor.close()
    conn.close()


def get_all_audit_logs():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            al.log_id,
            al.action,
            al.description,
            al.created_at,

            performer.full_name AS performed_by_name,
            target.full_name AS target_employee_name

        FROM audit_logs al
        LEFT JOIN employees performer
            ON al.performed_by = performer.employee_id
        LEFT JOIN employees target
            ON al.target_employee_id = target.employee_id

        ORDER BY al.created_at DESC
    """)

    logs = cursor.fetchall()

    cursor.close()
    conn.close()

    return logs