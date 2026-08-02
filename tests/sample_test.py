from config.database import get_db_connection

try:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT DATABASE();")
    print("Current Database:", cursor.fetchone())

    cursor.execute("SELECT VERSION();")
    print("TiDB Version:", cursor.fetchone())

    cursor.close()
    conn.close()

    print("✅ Connected to TiDB successfully!")

except Exception as e:
    print("❌ Connection failed")
    print(e)