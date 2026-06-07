from datetime import date, datetime, timedelta
import random
import csv
import secrets
import string
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import get_db_connection
from utils.password_utils import hash_password


TOTAL_EMPLOYEES = 50
CREDENTIALS_FILE = "employee_credentials.csv"


FIRST_NAMES = [
    "Rahul", "Ayesha", "Kiran", "Sneha", "Arjun", "Priya", "Sameer", "Anjali",
    "Rohit", "Neha", "Vikram", "Pooja", "Aditya", "Meena", "Sanjay", "Fatima",
    "Abdul", "Imran", "Nisha", "Varun"
]

LAST_NAMES = [
    "Sharma", "Khan", "Reddy", "Patel", "Verma", "Shaikh", "Naidu", "Gupta",
    "Rao", "Yadav", "Ali", "Das", "Singh", "Nair", "Babu", "Rahman"
]

JOB_TITLES = [
    "Data Analyst",
    "HR Executive",
    "Software Developer",
    "Accountant",
    "Sales Executive",
    "Operations Associate",
    "Business Analyst"
]


def generate_secure_password(length=12):
    chars = string.ascii_letters + string.digits + "@#$%&*!"
    return "".join(secrets.choice(chars) for _ in range(length))


def get_table_columns(cursor, table_name):
    cursor.execute(f"SHOW COLUMNS FROM {table_name}")
    return [row[0] for row in cursor.fetchall()]


def convert_mysql_time(time_value):
    if isinstance(time_value, timedelta):
        total_seconds = int(time_value.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return datetime.min.time().replace(
            hour=hours,
            minute=minutes,
            second=seconds
        )

    return time_value


def combine_datetime(work_date, time_value):
    proper_time = convert_mysql_time(time_value)
    return datetime.combine(work_date, proper_time)


def get_active_departments(cursor):
    cursor.execute("SELECT dept_id FROM departments WHERE is_active = TRUE")
    return [row[0] for row in cursor.fetchall()]


def get_active_shifts(cursor):
    cursor.execute("""
        SELECT shift_id, start_time, end_time, expected_hours, late_grace_minutes
        FROM shifts
        WHERE is_active = TRUE
    """)
    return cursor.fetchall()


def create_50_employees(cursor, conn):
    employee_columns = get_table_columns(cursor, "employees")
    departments = get_active_departments(cursor)
    shifts = get_active_shifts(cursor)

    if not departments:
        raise Exception("No active departments found.")

    if not shifts:
        raise Exception("No active shifts found.")

    credentials = []

    for i in range(1, TOTAL_EMPLOYEES + 1):
        full_name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        email = f"employee{i}@company.com"
        phone = f"98765{random.randint(10000, 99999)}"
        dept_id = random.choice(departments)
        shift_id = random.choice(shifts)[0]
        job_title = random.choice(JOB_TITLES)

        plain_password = generate_secure_password()
        password_hash = hash_password(plain_password)

        credentials.append({
            "employee_email": email,
            "temporary_password": plain_password
        })

        if "job_title" in employee_columns and "must_change_password" in employee_columns:
            cursor.execute("""
                INSERT INTO employees
                (
                    full_name,
                    email,
                    phone,
                    dept_id,
                    shift_id,
                    job_title,
                    password_hash,
                    role,
                    must_change_password
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'employee', TRUE)
            """, (
                full_name,
                email,
                phone,
                dept_id,
                shift_id,
                job_title,
                password_hash
            ))

        elif "job_title" in employee_columns:
            cursor.execute("""
                INSERT INTO employees
                (
                    full_name,
                    email,
                    phone,
                    dept_id,
                    shift_id,
                    job_title,
                    password_hash,
                    role
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'employee')
            """, (
                full_name,
                email,
                phone,
                dept_id,
                shift_id,
                job_title,
                password_hash
            ))

        elif "must_change_password" in employee_columns:
            cursor.execute("""
                INSERT INTO employees
                (
                    full_name,
                    email,
                    phone,
                    dept_id,
                    shift_id,
                    password_hash,
                    role,
                    must_change_password
                )
                VALUES (%s, %s, %s, %s, %s, %s, 'employee', TRUE)
            """, (
                full_name,
                email,
                phone,
                dept_id,
                shift_id,
                password_hash
            ))

        else:
            cursor.execute("""
                INSERT INTO employees
                (
                    full_name,
                    email,
                    phone,
                    dept_id,
                    shift_id,
                    password_hash,
                    role
                )
                VALUES (%s, %s, %s, %s, %s, %s, 'employee')
            """, (
                full_name,
                email,
                phone,
                dept_id,
                shift_id,
                password_hash
            ))

    conn.commit()

    with open(CREDENTIALS_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["employee_email", "temporary_password"]
        )
        writer.writeheader()
        writer.writerows(credentials)

    print("50 employees created successfully.")
    print(f"Temporary passwords saved to {CREDENTIALS_FILE}")


def calculate_attendance(work_date, shift):
    shift_id, start_time, end_time, expected_hours, late_grace_minutes = shift

    shift_start = combine_datetime(work_date, start_time)

    attendance_type = random.choices(
        ["Present", "Late", "Half Day", "Absent"],
        weights=[70, 15, 10, 5],
        k=1
    )[0]

    if attendance_type == "Absent":
        return None, None, 0, 0, "Absent", False, 0

    if attendance_type == "Present":
        check_in = shift_start + timedelta(minutes=random.randint(-15, 10))
        working_hours = round(random.uniform(8.0, 9.5), 2)
        status = "Present"
        is_late = False
        late_minutes = 0

    elif attendance_type == "Late":
        late_minutes = random.randint(late_grace_minutes + 1, 90)
        check_in = shift_start + timedelta(minutes=late_minutes)
        working_hours = round(random.uniform(7.0, 8.5), 2)
        status = "Present"
        is_late = True

    else:
        check_in = shift_start + timedelta(minutes=random.randint(-10, 30))
        working_hours = round(random.uniform(3.5, 4.5), 2)
        status = "Half Day"

        late_minutes = max(
            0,
            int((check_in - shift_start).total_seconds() // 60)
        )

        is_late = late_minutes > late_grace_minutes

    check_out = check_in + timedelta(hours=working_hours)
    overtime_hours = max(0, round(working_hours - float(expected_hours), 2))

    return (
        check_in,
        check_out,
        working_hours,
        overtime_hours,
        status,
        is_late,
        late_minutes
    )

# Add these two new functions before generate_attendance_records()

def generate_leave_requests(cursor, conn, employees, start_date, end_date):
    leave_types = ["Casual", "Sick", "Earned", "Unpaid"]
    statuses = ["Pending", "Approved", "Rejected"]

    leave_records = []

    for employee_id, shift_id in employees:
        number_of_leaves = random.randint(0, 3)

        for _ in range(number_of_leaves):
            leave_start = start_date + timedelta(
                days=random.randint(0, (end_date - start_date).days)
            )

            leave_duration = random.randint(1, 3)
            leave_end = leave_start + timedelta(days=leave_duration - 1)

            leave_type = random.choice(leave_types)

            status = random.choices(
                statuses,
                weights=[25, 60, 15],
                k=1
            )[0]

            reason = random.choice([
                "Personal work",
                "Medical reason",
                "Family function",
                "Travel requirement",
                "Health issue"
            ])

            reviewed_by = None
            reviewed_at = None
            admin_comment = None

            if status in ["Approved", "Rejected"]:
                reviewed_by = employees[0][0]
                reviewed_at = datetime.now()
                admin_comment = (
                    "Approved by admin"
                    if status == "Approved"
                    else "Rejected by admin"
                )

            leave_records.append((
                employee_id,
                leave_type,
                leave_start,
                leave_end,
                reason,
                status,
                reviewed_by,
                reviewed_at,
                admin_comment
            ))

    if leave_records:
        cursor.executemany("""
            INSERT INTO leave_requests
            (
                employee_id,
                leave_type,
                start_date,
                end_date,
                reason,
                status,
                reviewed_by,
                reviewed_at,
                admin_comment
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, leave_records)

        conn.commit()

    print(f"Leave requests inserted: {len(leave_records)}")


def generate_audit_logs(cursor, conn, employees):
    actions = [
        "Login",
        "Logout",
        "Check In",
        "Check Out",
        "Leave Applied",
        "Leave Approved",
        "Leave Rejected",
        "Password Reset"
    ]

    audit_records = []

    for employee_id, shift_id in employees:
        number_of_logs = random.randint(3, 8)

        for _ in range(number_of_logs):
            action = random.choice(actions)

            audit_records.append((
                employee_id,
                employee_id,
                action,
                f"Sample audit log generated for action: {action}"
            ))

    if audit_records:
        cursor.executemany("""
            INSERT INTO audit_logs
            (
                performed_by,
                target_employee_id,
                action,
                description
            )
            VALUES (%s, %s, %s, %s)
        """, audit_records)

        conn.commit()

    print(f"Audit logs inserted: {len(audit_records)}")

def generate_attendance_records():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        print("Deleting old audit logs...")
        cursor.execute("DELETE FROM audit_logs")

        print("Deleting old leave requests...")
        cursor.execute("DELETE FROM leave_requests")

        print("Deleting old attendance records...")
        cursor.execute("DELETE FROM attendance")

        print("Deleting old employee records...")
        cursor.execute("DELETE FROM employees")

        conn.commit()

        print("Creating new employees...")
        create_50_employees(cursor, conn)

        cursor.execute("""
            SELECT employee_id, shift_id
            FROM employees
            WHERE is_active = TRUE
            ORDER BY employee_id
            LIMIT %s
        """, (TOTAL_EMPLOYEES,))

        employees = cursor.fetchall()

        cursor.execute("""
            SELECT shift_id, start_time, end_time, expected_hours, late_grace_minutes
            FROM shifts
            WHERE is_active = TRUE
        """)

        shifts = {row[0]: row for row in cursor.fetchall()}

        end_date = date.today()
        start_date = end_date - timedelta(days=90)

        inserted_count = 0
        skipped_count = 0

        current_date = start_date

        print("Generating attendance records...")

        while current_date <= end_date:
            if current_date.weekday() == 6:
                current_date += timedelta(days=1)
                continue

            daily_records = []

            for employee_id, shift_id in employees:
                shift = shifts.get(shift_id)

                if not shift:
                    skipped_count += 1
                    continue

                (
                    check_in,
                    check_out,
                    working_hours,
                    overtime_hours,
                    status,
                    is_late,
                    late_minutes
                ) = calculate_attendance(current_date, shift)

                daily_records.append((
                    employee_id,
                    current_date,
                    check_in,
                    check_out,
                    working_hours,
                    overtime_hours,
                    status,
                    is_late,
                    late_minutes
                ))

            cursor.executemany("""
                INSERT INTO attendance
                (
                    employee_id,
                    work_date,
                    check_in,
                    check_out,
                    working_hours,
                    overtime_hours,
                    status,
                    is_late,
                    late_minutes
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, daily_records)

            conn.commit()

            inserted_count += len(daily_records)

            print(
                f"Completed date: {current_date} | "
                f"Records inserted: {len(daily_records)}"
            )

            current_date += timedelta(days=1)

        print("Generating leave requests...")
        generate_leave_requests(cursor, conn, employees, start_date, end_date)

        print("Generating audit logs...")
        generate_audit_logs(cursor, conn, employees)

        print("Attendance records generated successfully.")
        print(f"Employees created: {TOTAL_EMPLOYEES}")
        print(f"Attendance records inserted: {inserted_count}")
        print(f"Skipped records: {skipped_count}")
        print(f"Credentials file: {CREDENTIALS_FILE}")

    except Exception as e:
        print(f"Error: {e}")

        try:
            if conn.is_connected():
                conn.rollback()
        except:
            pass

    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass


if __name__ == "__main__":
    generate_attendance_records()