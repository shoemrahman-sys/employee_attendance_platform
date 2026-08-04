from config.database import read_cursor, write_cursor

def create_leave_request(employee_id, leave_type, start_date, end_date, reason):
    with write_cursor() as cursor:
        cursor.execute("""
            INSERT INTO leave_requests (
                employee_id,
                leave_type,
                start_date,
                end_date,
                reason
            )
            VALUES (%s, %s, %s, %s, %s)
        """, (
            employee_id,
            leave_type,
            start_date,
            end_date,
            reason
        ))

def get_employee_leave_requests(employee_id):
    with read_cursor(dictionary=True) as cursor:
        cursor.execute("""
            SELECT
                leave_id,
                leave_type,
                start_date,
                end_date,
                reason,
                status,
                admin_comment,
                created_at
            FROM leave_requests
            WHERE employee_id = %s
            ORDER BY created_at DESC
        """, (employee_id,))

        return cursor.fetchall()

def get_all_leave_requests():
    with read_cursor(dictionary=True) as cursor:
        cursor.execute("""
            SELECT
                lr.leave_id,
                lr.employee_id,
                e.full_name,
                e.email,
                lr.leave_type,
                lr.start_date,
                lr.end_date,
                lr.reason,
                lr.status,
                lr.admin_comment,
                lr.created_at,
                reviewer.full_name AS reviewed_by_name,
                lr.reviewed_at
            FROM leave_requests lr
            JOIN employees e
                ON lr.employee_id = e.employee_id
            LEFT JOIN employees reviewer
                ON lr.reviewed_by = reviewer.employee_id
            ORDER BY lr.created_at DESC
        """)

        return cursor.fetchall()

def update_leave_status(leave_id, status, reviewed_by, admin_comment=None,conn=None):
    with write_cursor(conn=conn) as cursor:
        cursor.execute("""
            UPDATE leave_requests
            SET
                status = %s,
                reviewed_by = %s,
                reviewed_at = CURRENT_TIMESTAMP,
                admin_comment = %s
            WHERE leave_id = %s
        """, (
            status,
            reviewed_by,
            admin_comment,
            leave_id
        ))

def get_leave_summary():
    with read_cursor(dictionary=True) as cursor:
        cursor.execute("""
            SELECT
                COUNT(*) AS total_leave_requests,

                SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) AS pending_leaves,

                SUM(CASE WHEN status = 'Approved' THEN 1 ELSE 0 END) AS approved_leaves,

                SUM(CASE WHEN status = 'Rejected' THEN 1 ELSE 0 END) AS rejected_leaves,

                SUM(
                    CASE
                        WHEN status = 'Approved'
                        AND CURDATE() BETWEEN start_date AND end_date
                        THEN 1 ELSE 0
                    END
                ) AS employees_on_leave_today

            FROM leave_requests
        """)

        return cursor.fetchone()

def get_employee_leave_summary(employee_id):
    with read_cursor(dictionary=True) as cursor:
        cursor.execute("""
            SELECT
                COUNT(*) AS total_leave_requests,

                SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) AS pending_leaves,

                SUM(CASE WHEN status = 'Approved' THEN 1 ELSE 0 END) AS approved_leaves,

                SUM(CASE WHEN status = 'Rejected' THEN 1 ELSE 0 END) AS rejected_leaves

            FROM leave_requests
            WHERE employee_id = %s
        """, (employee_id,))

        return cursor.fetchone()

def get_approved_leave_for_date(employee_id, target_date):
    with read_cursor(dictionary=True) as cursor:
        cursor.execute("""
            SELECT
                leave_id,
                leave_type,
                start_date,
                end_date,
                status
            FROM leave_requests
            WHERE employee_id = %s
              AND status = 'Approved'
              AND %s BETWEEN start_date AND end_date
            LIMIT 1
        """, (employee_id, target_date))

        return cursor.fetchone()