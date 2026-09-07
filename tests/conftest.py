import uuid

import pytest
from fastapi.testclient import TestClient

from backend.db import get_db_connection
from backend.main import app
from backend.security import (
    create_access_token,
    hash_password,
)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def authenticated_client():

    email = f"test_{uuid.uuid4().hex}@example.com"
    password = "TestPassword123"

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO users (
            name,
            email,
            password_hash
        )
        VALUES (%s, %s, %s)
        RETURNING id;
        """,
        (
            "Test User",
            email,
            hash_password(password),
        ),
    )

    user_id = cursor.fetchone()[0]

    connection.commit()

    cursor.close()
    connection.close()

    token = create_access_token(user_id)

    try:

        with TestClient(app) as test_client:

            test_client.headers.update(
                {
                    "Authorization": f"Bearer {token}",
                }
            )

            yield test_client

    finally:

        cleanup_connection = get_db_connection()
        cleanup_cursor = cleanup_connection.cursor()

        cleanup_cursor.execute(
            """
            DELETE FROM budgets
            WHERE user_id = %s;
            """,
            (user_id,),
        )

        cleanup_cursor.execute(
            """
            DELETE FROM expenses
            WHERE user_id = %s;
            """,
            (user_id,),
        )

        cleanup_cursor.execute(
            """
            DELETE FROM users
            WHERE id = %s;
            """,
            (user_id,),
        )

        cleanup_connection.commit()

        cleanup_cursor.close()
        cleanup_connection.close()

@pytest.fixture
def cleanup_user():
    created_emails = []

    def register_email(email):
        created_emails.append(email)

    yield register_email

    connection = get_db_connection()
    cursor = connection.cursor()

    for email in created_emails:
        cursor.execute(
            """
            DELETE FROM users
            WHERE email = %s;
            """,
            (email,)
        )

    connection.commit()

    cursor.close()
    connection.close()
