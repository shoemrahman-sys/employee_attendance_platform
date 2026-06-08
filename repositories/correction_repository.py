from config.database import get_db_connection


def create_correction_request(
    employee_id,
    attendance_id,
    requested_check_in,
    requested_check_out,
    reason
):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO attendance_correction_requests (
            employee_id,
            attendance_id,
            requested_check_in,
            requested_check_out,
            reason
        )
        VALUES (%s, %s, %s, %s, %s)
    """, (
        employee_id,
        attendance_id,
        requested_check_in,
        requested_check_out,
        reason
    ))

    conn.commit()
    cursor.close()
    conn.close()


def get_employee_correction_requests(employee_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            correction_id,
            attendance_id,
            requested_check_in,
            requested_check_out,
            reason,
            status,
            admin_comment,
            created_at
        FROM attendance_correction_requests
        WHERE employee_id = %s
        ORDER BY created_at DESC
    """, (employee_id,))

    records = cursor.fetchall()
    cursor.close()
    conn.close()
    return records


def get_all_correction_requests():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            acr.correction_id,
            acr.employee_id,
            e.full_name,
            e.email,
            acr.attendance_id,
            a.work_date,
            a.check_in AS current_check_in,
            a.check_out AS current_check_out,
            acr.requested_check_in,
            acr.requested_check_out,
            acr.reason,
            acr.status,
            acr.admin_comment,
            acr.reviewed_at,
            acr.created_at
        FROM attendance_correction_requests acr
        JOIN employees e ON acr.employee_id = e.employee_id
        JOIN attendance a ON acr.attendance_id = a.attendance_id
        ORDER BY acr.created_at DESC
    """)

    records = cursor.fetchall()
    cursor.close()
    conn.close()
    return records


def update_correction_status(correction_id, status, reviewed_by, admin_comment=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE attendance_correction_requests
        SET
            status = %s,
            reviewed_by = %s,
            reviewed_at = CURRENT_TIMESTAMP,
            admin_comment = %s
        WHERE correction_id = %s
    """, (
        status,
        reviewed_by,
        admin_comment,
        correction_id
    ))

    conn.commit()
    cursor.close()
    conn.close()