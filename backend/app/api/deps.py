from fastapi import Depends
from app.db.connection import execute_one, execute_returning

# --- AUTH BYPASS FOR DEMO ---
def get_current_user():
    """Bypasses JWT auth and always returns a mock admin user."""
    # Check if our bypass admin exists
    admin_email = "admin@bypass.com"
    user = execute_one("SELECT id, email, full_name, role FROM users WHERE email = %s", (admin_email,))
    
    if not user:
        # Create the bypass admin on the fly
        user = execute_returning(
            """
            INSERT INTO users (email, hashed_password, full_name, role)
            VALUES (%s, 'bypass', 'Admin Bypass', 'admin')
            RETURNING id, email, full_name, role
            """,
            (admin_email,)
        )
    return user

