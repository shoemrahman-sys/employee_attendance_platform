from config.database import get_db_connection


def create_leave_request(employee_id, leave_type, start_date, end_date, reason):
    conn = get_db_connection()
    cursor = conn.cursor()

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

    conn.commit()
    cursor.close()
    conn.close()


def get_employee_leave_requests(employee_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

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

    leaves = cursor.fetchall()

    cursor.close()
    conn.close()

    return leaves


def get_all_leave_requests():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

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

    leaves = cursor.fetchall()

    cursor.close()
    conn.close()

    return leaves


def update_leave_status(leave_id, status, reviewed_by, admin_comment=None):
    conn = get_db_connection()
    cursor = conn.cursor()

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

    conn.commit()
    cursor.close()
    conn.close()

def get_leave_summary():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

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

    summary = cursor.fetchone()

    cursor.close()
    conn.close()

    return summary

def get_employee_leave_summary(employee_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            COUNT(*) AS total_leave_requests,

            SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) AS pending_leaves,

            SUM(CASE WHEN status = 'Approved' THEN 1 ELSE 0 END) AS approved_leaves,

            SUM(CASE WHEN status = 'Rejected' THEN 1 ELSE 0 END) AS rejected_leaves

        FROM leave_requests
        WHERE employee_id = %s
    """, (employee_id,))

    summary = cursor.fetchone()

    cursor.close()
    conn.close()

    return summary

def get_approved_leave_for_date(employee_id, target_date):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

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

    leave = cursor.fetchone()

    cursor.close()
    conn.close()

    return leave