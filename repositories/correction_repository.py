from config.database import read_cursor, write_cursor

def create_correction_request(
    employee_id,
    attendance_id,
    requested_check_in,
    requested_check_out,
    reason
):
    with write_cursor() as cursor:
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

def get_employee_correction_requests(employee_id):
    with read_cursor(dictionary=True) as cursor:
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

        return cursor.fetchall()

def get_all_correction_requests():
    with read_cursor(dictionary=True) as cursor:
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
            JOIN employees e
                ON acr.employee_id = e.employee_id
            JOIN attendance a
                ON acr.attendance_id = a.attendance_id
            ORDER BY acr.created_at DESC
        """)

        return cursor.fetchall()

def update_correction_status(
    correction_id,
    status,
    reviewed_by,
    admin_comment=None,
    conn=None
):
    with write_cursor(conn=conn) as cursor:
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