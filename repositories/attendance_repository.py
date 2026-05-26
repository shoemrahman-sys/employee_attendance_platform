from config.database import get_db_connection


def get_today_attendance(employee_id, attendance_date):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT *
        FROM attendance
        WHERE employee_id = %s
        AND attendance_date = %s
    """

    cursor.execute(query, (employee_id, attendance_date))

    attendance = cursor.fetchone()

    cursor.close()
    connection.close()

    return attendance


def create_check_in(employee_id, attendance_date, check_in_time):
    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        INSERT INTO attendance
        (
            employee_id,
            attendance_date,
            check_in_time,
            status
        )
        VALUES (%s, %s, %s, %s)
    """

    values = (
        employee_id,
        attendance_date,
        check_in_time,
        "Checked In"
    )

    cursor.execute(query, values)

    connection.commit()

    cursor.close()
    connection.close()


def update_check_out(
    attendance_id,
    check_out_time,
    working_hours
):
    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        UPDATE attendance
        SET check_out_time = %s,
            working_hours = %s,
            status = %s
        WHERE attendance_id = %s
    """

    values = (
        check_out_time,
        working_hours,
        "Checked Out",
        attendance_id
    )

    cursor.execute(query, values)

    connection.commit()

    cursor.close()
    connection.close()