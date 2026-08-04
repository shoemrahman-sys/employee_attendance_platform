import os
from contextlib import contextmanager

from dotenv import load_dotenv
from mysql.connector import pooling

load_dotenv()

# ----------------------------------------
# MySQL Connection Pool
# ----------------------------------------

connection_pool = pooling.MySQLConnectionPool(
    pool_name="attendance_pool",
    pool_size=10,
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    ssl_disabled=False
)


# ----------------------------------------
# Get Connection From Pool
# ----------------------------------------

def get_db_connection():
    return connection_pool.get_connection()


# ----------------------------------------
# Read Cursor (SELECT Queries)
# ----------------------------------------

@contextmanager
def read_cursor(dictionary=False):
    conn = get_db_connection()
    cursor = None

    try:
        cursor = conn.cursor(dictionary=dictionary)
        yield cursor

    finally:
        if cursor is not None:
            cursor.close()

        conn.close()


# ----------------------------------------
# Write Cursor (INSERT / UPDATE / DELETE)
# ----------------------------------------

@contextmanager
def write_cursor(dictionary=False, conn=None):
    """
    If conn is None:
        - Creates its own connection
        - Auto commits
        - Auto rollbacks
        - Auto closes

    If conn is provided:
        - Uses existing connection
        - Does NOT commit
        - Does NOT rollback
        - Does NOT close
        (Caller manages transaction)
    """

    own_connection = conn is None

    if own_connection:
        conn = get_db_connection()

    cursor = conn.cursor(dictionary=dictionary)

    try:
        yield cursor

        if own_connection:
            conn.commit()

    except Exception:
        if own_connection:
            conn.rollback()
        raise

    finally:
        cursor.close()

        if own_connection:
            conn.close()

def get_transaction_connection():
    """
    Returns a pooled connection for multi-step transactions.
    Caller is responsible for commit/rollback/close.
    """
    return get_db_connection()