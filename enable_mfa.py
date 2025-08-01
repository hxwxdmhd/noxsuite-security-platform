import pymysql


def enable_mfa_for_test_user():
    try:
        conn = pymysql.connect("./database/noxsuite.db")
        cursor = conn.cursor()

        # Check if the user exists
        cursor.execute(
            "SELECT id, username FROM users WHERE email = 'mfa_test@noxsuite.local'"
        )
        user = cursor.fetchone()

        if user:
            user_id, username = user
            print(f"Found user: {username} (ID: {user_id})")

            # Enable MFA for the user
            cursor.execute(
                "UPDATE users SET mfa_enabled = 1, mfa_secret = 'ABCDEFGHIJKLMNOP' WHERE id = ?",
                (user_id,),
            )
            conn.commit()
            print(f"MFA enabled for user {username}")

            # Verify the update
            cursor.execute(
                "SELECT mfa_enabled, mfa_secret FROM users WHERE id = ?", (
                    user_id,)
            )
            mfa_status = cursor.fetchone()
            print(
                f"MFA status: enabled={mfa_status[0]}, secret={mfa_status[1]}")
        else:
            print("Test user not found")

            # List all users
            cursor.execute(
                "SELECT id, username, email, mfa_enabled FROM users")
            users = cursor.fetchall()
            print("\nAll users in database:")
            for user in users:
                print(
                    f"ID: {user[0]}, Username: {user[1]}, Email: {user[2]}, MFA Enabled: {user[3]}"
                )
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    enable_mfa_for_test_user()
