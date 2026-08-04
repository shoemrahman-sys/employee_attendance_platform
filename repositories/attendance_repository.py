from datetime import date
from config.database import read_cursor, write_cursor

def get_today_attendance(employee_id):
    with read_cursor(dictionary=True) as cursor:
        cursor.execute("""
            SELECT *
            FROM attendance
            WHERE employee_id = %s
              AND work_date = %s
        """, (employee_id, date.today()))

        return cursor.fetchone()

def create_check_in(employee_id, work_date, check_in, is_late, late_minutes):
    with write_cursor() as cursor:
        cursor.execute("""
            INSERT INTO attendance
            (employee_id, work_date, check_in, is_late, late_minutes, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            employee_id,
            work_date,
            check_in,
            is_late,
            late_minutes,
            "Present"
        ))

def update_check_out(
    attendance_id,
    check_out,
    working_hours,
    overtime_hours,
    status
):
    with write_cursor() as cursor:
        cursor.execute("""
            UPDATE attendance
            SET
                check_out = %s,
                working_hours = %s,
                overtime_hours = %s,
                status = %s
            WHERE attendance_id = %s
        """, (
            check_out,
            working_hours,
            overtime_hours,
            status,
            attendance_id
        ))

def get_employee_attendance_history(employee_id):
    with read_cursor(dictionary=True) as cursor:
        cursor.execute("""
            SELECT
                attendance_id,
                work_date,
                check_in,
                check_out,
                working_hours,
                overtime_hours,
                status,
                is_late,
                late_minutes
            FROM attendance
            WHERE employee_id = %s
            ORDER BY work_date DESC
        """, (employee_id,))

        return cursor.fetchall()

def get_all_attendance_records():
    with read_cursor(dictionary=True) as cursor:
        cursor.execute("""
            SELECT
                a.attendance_id,
                e.full_name,
                d.dept_name,
                s.shift_name,
                a.work_date,
                a.check_in,
                a.check_out,
                a.working_hours,
                a.overtime_hours,
                a.status,
                a.is_late,
                a.late_minutes
            FROM attendance a
            JOIN employees e
                ON a.employee_id = e.employee_id
            LEFT JOIN departments d
                ON e.dept_id = d.dept_id
            LEFT JOIN shifts s
                ON e.shift_id = s.shift_id
            ORDER BY a.work_date DESC
        """)

        return cursor.fetchall()

def get_admin_summary():
    with read_cursor(dictionary=True) as cursor:

        cursor.execute("""
            SELECT COUNT(*) AS total_employees
            FROM employees
            WHERE is_active = TRUE
        """)
        total_employees = cursor.fetchone()["total_employees"]

        cursor.execute("""
            SELECT
                SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) AS present_today,
                SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END) AS absent_today,
                SUM(CASE WHEN status = 'Half Day' THEN 1 ELSE 0 END) AS half_day_today,
                SUM(CASE WHEN is_late = TRUE THEN 1 ELSE 0 END) AS late_today,
                ROUND(AVG(working_hours), 2) AS avg_working_hours,
                ROUND(SUM(overtime_hours), 2) AS total_overtime
            FROM attendance
            WHERE work_date = CURDATE()
        """)

        summary = cursor.fetchone()

        return {
            "total_employees": total_employees,
            "present_today": summary["present_today"] or 0,
            "absent_today": summary["absent_today"] or 0,
            "half_day_today": summary["half_day_today"] or 0,
            "late_today": summary["late_today"] or 0,
            "avg_working_hours": summary["avg_working_hours"] or 0,
            "total_overtime": summary["total_overtime"] or 0,
        }

def update_attendance_correction(
    attendance_id,
    check_in,
    check_out,
    conn=None
):
    with write_cursor(conn=conn) as cursor:

        cursor.execute("""
            UPDATE attendance
            SET
                check_in = %s,
                check_out = %s,
                working_hours = TIMESTAMPDIFF(MINUTE, %s, %s) / 60,
                overtime_hours = GREATEST(
                    (TIMESTAMPDIFF(MINUTE, %s, %s) / 60) - 8,
                    0
                ),
                status = CASE
                    WHEN TIMESTAMPDIFF(MINUTE, %s, %s) / 60 >= 8 THEN 'Present'
                    WHEN TIMESTAMPDIFF(MINUTE, %s, %s) / 60 >= 4 THEN 'Half Day'
                    ELSE 'Absent'
                END
            WHERE attendance_id = %s
        """, (
            check_in,
            check_out,
            check_in,
            check_out,
            check_in,
            check_out,
            check_in,
            check_out,
            check_in,
            check_out,
            attendance_id
        ))

def get_attendance_by_id(attendance_id):
    with read_cursor(dictionary=True) as cursor:

        cursor.execute("""
            SELECT
                attendance_id,
                employee_id,
                work_date,
                check_in,
                check_out,
                working_hours,
                overtime_hours,
                status
            FROM attendance
            WHERE attendance_id = %s
        """, (attendance_id,))

        return cursor.fetchone()