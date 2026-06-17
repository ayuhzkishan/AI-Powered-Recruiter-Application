from app.db.connection import execute_one, execute_returning


def get_user_by_email(email: str):
    return execute_one(
        "SELECT id, email, hashed_password, full_name, role FROM users WHERE email = %s",
        (email,),
    )


def get_user_by_id(user_id: str):
    return execute_one(
        "SELECT id, email, full_name, role FROM users WHERE id = %s",
        (user_id,),
    )


def create_user(email: str, hashed_password: str, full_name: str) -> dict:
    return execute_returning(
        """
        INSERT INTO users (email, hashed_password, full_name)
        VALUES (%s, %s, %s)
        RETURNING id, email, full_name, created_at
        """,
        (email, hashed_password, full_name),
    )
