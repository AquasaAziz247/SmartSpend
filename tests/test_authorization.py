import uuid

from backend.db import get_db_connection


def create_test_user(
    client,
    name
):

    email = (
        f"authorization_{uuid.uuid4().hex}"
        "@example.com"
    )

    response = client.post(
        "/users/register",
        json={
            "name": name,
            "email": email,
            "password": "TestPassword123"
        }
    )

    assert response.status_code == 201

    login_response = client.post(
        "/users/login",
        data={
            "username": email,
            "password": "TestPassword123"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    return email, headers


def cleanup_test_user(email):

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM users
        WHERE email = %s;
        """,
        (email,)
    )

    result = cursor.fetchone()

    if result:

        user_id = result[0]

        cursor.execute(
            """
            DELETE FROM budgets
            WHERE user_id = %s;
            """,
            (user_id,)
        )

        cursor.execute(
            """
            DELETE FROM expenses
            WHERE user_id = %s;
            """,
            (user_id,)
        )

        cursor.execute(
            """
            DELETE FROM users
            WHERE id = %s;
            """,
            (user_id,)
        )

    connection.commit()

    cursor.close()
    connection.close()


def test_user_cannot_get_another_users_expense(
    client
):

    user_a_email, user_a_headers = create_test_user(
        client,
        "Authorization User A"
    )

    user_b_email, user_b_headers = create_test_user(
        client,
        "Authorization User B"
    )

    try:

        response = client.post(
            "/expenses",
            headers=user_b_headers,
            json={
                "amount": 500.00,
                "category": "Private",
                "description": "User B private expense",
                "expense_date": "2026-09-06"
            }
        )

        assert response.status_code == 201

        expense_id = response.json()["id"]

        response = client.get(
            f"/expenses/{expense_id}",
            headers=user_a_headers
        )

        assert response.status_code == 404

    finally:

        cleanup_test_user(user_a_email)
        cleanup_test_user(user_b_email)


def test_user_cannot_update_another_users_expense(
    client
):

    user_a_email, user_a_headers = create_test_user(
        client,
        "Authorization User A"
    )

    user_b_email, user_b_headers = create_test_user(
        client,
        "Authorization User B"
    )

    try:

        response = client.post(
            "/expenses",
            headers=user_b_headers,
            json={
                "amount": 500.00,
                "category": "Private",
                "description": "User B private expense",
                "expense_date": "2026-09-06"
            }
        )

        assert response.status_code == 201

        expense_id = response.json()["id"]

        response = client.put(
            f"/expenses/{expense_id}",
            headers=user_a_headers,
            json={
                "amount": 999.99,
                "category": "Hacked",
                "description": "Unauthorized update",
                "expense_date": "2026-09-06"
            }
        )

        assert response.status_code == 404

    finally:

        cleanup_test_user(user_a_email)
        cleanup_test_user(user_b_email)


def test_user_cannot_delete_another_users_expense(
    client
):

    user_a_email, user_a_headers = create_test_user(
        client,
        "Authorization User A"
    )

    user_b_email, user_b_headers = create_test_user(
        client,
        "Authorization User B"
    )

    try:

        response = client.post(
            "/expenses",
            headers=user_b_headers,
            json={
                "amount": 500.00,
                "category": "Private",
                "description": "User B private expense",
                "expense_date": "2026-09-06"
            }
        )

        assert response.status_code == 201

        expense_id = response.json()["id"]

        response = client.delete(
            f"/expenses/{expense_id}",
            headers=user_a_headers
        )

        assert response.status_code == 404

        response = client.get(
            f"/expenses/{expense_id}",
            headers=user_b_headers
        )

        assert response.status_code == 200

    finally:

        cleanup_test_user(user_a_email)
        cleanup_test_user(user_b_email)


def test_user_cannot_update_another_users_budget(
    client
):

    user_a_email, user_a_headers = create_test_user(
        client,
        "Authorization User A"
    )

    user_b_email, user_b_headers = create_test_user(
        client,
        "Authorization User B"
    )

    try:

        response = client.post(
            "/budgets",
            headers=user_b_headers,
            json={
                "category": "Private",
                "amount": 3000.00,
                "month": 9,
                "year": 2026
            }
        )

        assert response.status_code == 201

        budget_id = response.json()["id"]

        response = client.put(
            f"/budgets/{budget_id}",
            headers=user_a_headers,
            json={
                "category": "Hacked",
                "amount": 9999.99,
                "month": 9,
                "year": 2026
            }
        )

        assert response.status_code == 404

    finally:

        cleanup_test_user(user_a_email)
        cleanup_test_user(user_b_email)


def test_user_cannot_delete_another_users_budget(
    client
):

    user_a_email, user_a_headers = create_test_user(
        client,
        "Authorization User A"
    )

    user_b_email, user_b_headers = create_test_user(
        client,
        "Authorization User B"
    )

    try:

        response = client.post(
            "/budgets",
            headers=user_b_headers,
            json={
                "category": "Private",
                "amount": 3000.00,
                "month": 9,
                "year": 2026
            }
        )

        assert response.status_code == 201

        budget_id = response.json()["id"]

        response = client.delete(
            f"/budgets/{budget_id}",
            headers=user_a_headers
        )

        assert response.status_code == 404

        response = client.get(
            "/budgets",
            headers=user_b_headers
        )

        assert response.status_code == 200

        budgets = response.json()

        assert any(
            budget["id"] == budget_id
            for budget in budgets
        )

    finally:

        cleanup_test_user(user_a_email)
        cleanup_test_user(user_b_email)


def test_user_cannot_see_another_users_analytics(
    client
):

    user_a_email, user_a_headers = create_test_user(
        client,
        "Analytics User A"
    )

    user_b_email, user_b_headers = create_test_user(
        client,
        "Analytics User B"
    )

    try:

        response = client.post(
            "/expenses",
            headers=user_b_headers,
            json={
                "amount": 9999.99,
                "category": "Private",
                "description": "User B private spending",
                "expense_date": "2026-09-06"
            }
        )

        assert response.status_code == 201

        response = client.get(
            "/analytics/summary",
            headers=user_a_headers
        )

        assert response.status_code == 200

        summary = response.json()

        assert summary["total_spending"] is None
        assert summary["expense_count"] == 0

        response = client.get(
            "/analytics/categories",
            headers=user_a_headers
        )

        assert response.status_code == 200
        assert response.json() == []

        response = client.get(
            "/analytics/monthly",
            headers=user_a_headers
        )

        assert response.status_code == 200
        assert response.json() == []

        response = client.get(
            "/analytics/trends",
            headers=user_a_headers
        )

        assert response.status_code == 200
        assert response.json() == []

    finally:

        cleanup_test_user(user_a_email)
        cleanup_test_user(user_b_email)


def test_user_cannot_see_another_users_insights(
    client
):

    user_a_email, user_a_headers = create_test_user(
        client,
        "Insights User A"
    )

    user_b_email, user_b_headers = create_test_user(
        client,
        "Insights User B"
    )

    try:

        response = client.post(
            "/budgets",
            headers=user_b_headers,
            json={
                "category": "Private",
                "amount": 100.00,
                "month": 9,
                "year": 2026
            }
        )

        assert response.status_code == 201

        response = client.post(
            "/expenses",
            headers=user_b_headers,
            json={
                "amount": 150.00,
                "category": "Private",
                "description": "Over budget",
                "expense_date": "2026-09-06"
            }
        )

        assert response.status_code == 201

        response = client.get(
            "/insights",
            headers=user_a_headers
        )

        assert response.status_code == 200

        assert response.json() == []

    finally:

        cleanup_test_user(user_a_email)
        cleanup_test_user(user_b_email)