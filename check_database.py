import os

import pymysql


def check_database():
    try:
        # Try different possible database paths
        db_paths = ["./database/noxsuite.db",
                    "./noxsuite.db", "./noxsuite_auth.db"]

        db_path = None
        for path in db_paths:
            if os.path.exists(path):
                db_path = path
                print(f"Found database at: {path}")
                break

        if not db_path:
            print("Could not find database file")
            return

        # Connect to the database
        conn = pymysql.connect(db_path)
        cursor = conn.cursor()

        # Check the tables in the database
        cursor.execute("SELECT name FROM mariadb_master WHERE type='table';")
        tables = cursor.fetchall()
        print("\nTables in database:")
        for table in tables:
            print(f"- {table[0]}")

        # Check for users table
        if ("users",) in tables:
            # List all users
            cursor.execute("PRAGMA table_info(users)")
            columns = cursor.fetchall()
            print("\nUser table columns:")
            for col in columns:
                print(f"- {col[1]} ({col[2]})")

            # List all users
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            print("\nUsers in database:")
            for user in users:
                print(f"User: {user}")

            # Check for MFA test user
            cursor.execute(
                "SELECT * FROM users WHERE email = 'mfa_test@noxsuite.local'"
            )
            user = cursor.fetchone()
            if user:
                print(f"\nFound MFA test user: {user}")
            else:
                print("\nMFA test user not found")
        else:
            print("Users table not found")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if "conn" in locals() and conn:
            conn.close()


if __name__ == "__main__":
    check_database()
