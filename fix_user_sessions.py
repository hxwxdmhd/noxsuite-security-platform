#!/usr/bin/env python3
"""
Fix User Sessions for NoxSuite
=============================
Fix unique constraint issues with user sessions.
"""

import os
import secrets
import sys
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import database models
try:
    from backend.models.user import Base, SessionLocal, User, UserSession, engine
except ImportError:
    print(
        "Error: Cannot import database models. Make sure you have run setup_database_simple.py first."
    )
    sys.exit(1)


def fix_user_sessions():
    """Fix user sessions"""
    db = SessionLocal()

    try:
        print("Checking for duplicate refresh tokens...")

        # Find all user sessions
        all_sessions = db.query(UserSession).all()
        print(f"Found {len(all_sessions)} user sessions")

        # Group sessions by refresh token to find duplicates
        sessions_by_token = {}
        for session in all_sessions:
            if session.refresh_token in sessions_by_token:
                sessions_by_token[session.refresh_token].append(session)
            else:
                sessions_by_token[session.refresh_token] = [session]

        # Identify tokens with duplicates
        duplicates = {
            token: sessions
            for token, sessions in sessions_by_token.items()
            if len(sessions) > 1
        }

        if not duplicates:
            print("No duplicate refresh tokens found. All good!")
            return

        print(f"Found {len(duplicates)} tokens with duplicates")
        fixed_count = 0

        # Fix duplicates by making tokens unique
        for token, dup_sessions in duplicates.items():
            print(
                f"Fixing {len(dup_sessions)} duplicate sessions for token: {token[:10]}..."
            )

            # Keep first session as is, update the rest with unique tokens
            for i, session in enumerate(dup_sessions[1:], 1):
                unique_id = secrets.token_hex(8)
                new_token = f"{unique_id}_{token[:40]}"
                print(
                    f"  Session {session.id}: {token[:10]} -> {new_token[:10]}")
                session.refresh_token = new_token
                fixed_count += 1

        # Commit changes
        db.commit()
        print(f"Fixed {fixed_count} duplicate sessions")

    except Exception as e:
        db.rollback()
        print(f"Error fixing user sessions: {str(e)}")

    finally:
        db.close()


if __name__ == "__main__":
    print("=== NoxSuite User Sessions Fix ===")
    fix_user_sessions()
    print("Done!")
