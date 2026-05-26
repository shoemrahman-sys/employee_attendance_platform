from config.database import get_db_connection

def create_employee(full_name, email, phone, department, password_hash):
    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        INSERT INTO employees
        (full_name, email, phone, department, password_hash)
        VALUES (%s, %s, %s, %s, %s)
    """

    cursor.execute(query, (full_name, email, phone, department, password_hash))
    connection.commit()

    cursor.close()
    connection.close()


def get_employee_by_email(email):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT employee_id, full_name, email, password_hash, role
        FROM employees
        WHERE email = %s
    """

    cursor.execute(query, (email,))
    employee = cursor.fetchone()

    cursor.close()
    connection.close()

    return employee