from config.database import read_cursor, write_cursor

def get_login_attempt(email):
    with read_cursor(dictionary=True) as cursor:
        cursor.execute("""
            SELECT *
            FROM login_attempts
            WHERE email = %s
        """, (email,))

        return cursor.fetchone()

def create_login_attempt(email):
    with write_cursor() as cursor:
        cursor.execute("""
            INSERT IGNORE INTO login_attempts (email)
            VALUES (%s)
        """, (email,))

def record_failed_attempt(email):
    with write_cursor() as cursor:
        cursor.execute("""
            UPDATE login_attempts
            SET
                failed_attempts = failed_attempts + 1,
                last_attempt = CURRENT_TIMESTAMP,
                locked_until = CASE
                    WHEN failed_attempts + 1 >= 5
                    THEN DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 10 MINUTE)
                    ELSE locked_until
                END
            WHERE email = %s
        """, (email,))

def reset_login_attempts(email):
    with write_cursor() as cursor:
        cursor.execute("""
            UPDATE login_attempts
            SET
                failed_attempts = 0,
                locked_until = NULL
            WHERE email = %s
        """, (email,))