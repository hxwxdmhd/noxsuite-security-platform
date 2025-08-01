#!/usr/bin/env python3
"""
Create Admin User
================
Creates the admin user for testing.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.models.user import User, Role, UserRole, SessionLocal, Base, engine

def create_admin_user():
    """Create admin user and roles"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if admin exists
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("Admin user already exists")
        else:
            # Create roles
            admin_role = Role(
                name="admin",
                description="System Administrator",
                permissions='["users:read", "users:write", "roles:read", "roles:write", "audit:read"]'
            )
            db.add(admin_role)
            
            user_role = Role(
                name="user", 
                description="Standard User",
                permissions='["profile:read", "profile:write"]'
            )
            db.add(user_role)
            db.commit()
            
            # Create admin user
            admin_user = User(
                username="admin",
                email="admin@noxsuite.local",
                password_hash=User.hash_password("Admin123!"),
                is_active=True,
                is_verified=True
        )
        db.add(admin_user)
        db.commit()
        
        # Assign admin role
        user_role_assignment = UserRole(
            user_id=admin_user.id,
            role_id=admin_role.id
        )
        db.add(user_role_assignment)
        db.commit()
        
        print("✓ Admin user created successfully")
        print("  Email: admin@noxsuite.local")
        print("  Password: Admin123!")
        
        # Create regular user for testing
        existing_user = db.query(User).filter(User.username == "user").first()
        if not existing_user:
            # Create regular user
            regular_user = User(
                username="user",
                email="user@noxsuite.local",
                password_hash=User.hash_password("User123!"),
                is_active=True,
                is_verified=True
            )
            db.add(regular_user)
            db.commit()
            
            # Assign user role
            regular_user_role = UserRole(
                user_id=regular_user.id,
                role_id=user_role.id
            )
            db.add(regular_user_role)
            db.commit()
            
            print("✓ Regular user created successfully")
            print("  Email: user@noxsuite.local")
            print("  Password: User123!")
        else:
            print("Regular user already exists")
        
        # Create MFA test user
        mfa_username = "mfa_test"
        existing_mfa_user = db.query(User).filter(User.username == mfa_username).first()
        if not existing_mfa_user:
            # Create MFA test user
            mfa_user = User(
                username=mfa_username,
                email="mfa_test@noxsuite.local",
                password_hash=User.hash_password("Mfa123!"),
                is_active=True,
                is_verified=True
            )
            db.add(mfa_user)
            db.commit()
            
            # Assign user role
            mfa_user_role = UserRole(
                user_id=mfa_user.id,
                role_id=user_role.id
            )
            db.add(mfa_user_role)
            db.commit()
            
            print("✓ MFA test user created successfully")
            print("  Email: mfa_test@noxsuite.local")
            print("  Password: Mfa123!")
        else:
            print("MFA test user already exists")
    except Exception as e:
        print(f"Error creating users: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
