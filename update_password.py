import bcrypt
import pymysql


def update_user_password():
    try:
        conn = pymysql.connect("./database/noxsuite.db")
        cursor = conn.cursor()

        # Hash the new password
        password = "MfaUser123!"
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"), salt).decode("utf-8")

        # Update the user's password
        cursor.execute(
            "UPDATE users SET password_hash = ? WHERE email = 'mfa_test@noxsuite.local'",
            (hashed_password,),
        )
        conn.commit()

        # Verify the update
        cursor.execute(
            "SELECT username, email, password_hash FROM users WHERE email = 'mfa_test@noxsuite.local'"
        )
        user = cursor.fetchone()
        if user:
            print(f"Updated password for user: {user[0]} ({user[1]})")
            print(f"New password hash: {user[2]}")
        else:
            print("User not found")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    update_user_password()
