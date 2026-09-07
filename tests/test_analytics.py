from decimal import Decimal


def test_summary_calculations(
    authenticated_client
):

    expenses = [
        {
            "amount": 100.00,
            "category": "Food",
            "description": "Breakfast",
            "expense_date": "2026-09-01"
        },
        {
            "amount": 200.00,
            "category": "Travel",
            "description": "Taxi",
            "expense_date": "2026-09-02"
        },
        {
            "amount": 300.00,
            "category": "Food",
            "description": "Dinner",
            "expense_date": "2026-09-03"
        }
    ]

    for expense in expenses:

        response = authenticated_client.post(
            "/expenses",
            json=expense
        )

        assert response.status_code == 201

    response = authenticated_client.get(
        "/analytics/summary"
    )

    assert response.status_code == 200

    data = response.json()

    assert Decimal(
        str(data["total_spending"])
    ) == Decimal("600.00")

    assert data["expense_count"] == 3

    assert Decimal(
        str(data["average_expense"])
    ) == Decimal("200.00")

    assert Decimal(
        str(data["highest_expense"])
    ) == Decimal("300.00")

    assert Decimal(
        str(data["lowest_expense"])
    ) == Decimal("100.00")


def test_empty_summary_returns_null_values(
    authenticated_client
):

    response = authenticated_client.get(
        "/analytics/summary"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_spending"] is None
    assert data["expense_count"] == 0
    assert data["average_expense"] is None
    assert data["highest_expense"] is None
    assert data["lowest_expense"] is None


def test_category_analytics_with_multiple_categories(
    authenticated_client
):

    expenses = [
        {
            "amount": 100.00,
            "category": "Food",
            "description": "Breakfast",
            "expense_date": "2026-09-01"
        },
        {
            "amount": 300.00,
            "category": "Food",
            "description": "Dinner",
            "expense_date": "2026-09-02"
        },
        {
            "amount": 200.00,
            "category": "Travel",
            "description": "Taxi",
            "expense_date": "2026-09-03"
        }
    ]

    for expense in expenses:

        response = authenticated_client.post(
            "/expenses",
            json=expense
        )

        assert response.status_code == 201

    response = authenticated_client.get(
        "/analytics/categories"
    )

    assert response.status_code == 200

    categories = response.json()

    assert len(categories) == 2

    assert categories[0]["category"] == "Food"

    assert Decimal(
        str(categories[0]["total_spending"])
    ) == Decimal("400.00")

    assert categories[0]["expense_count"] == 2

    assert categories[1]["category"] == "Travel"

    assert Decimal(
        str(categories[1]["total_spending"])
    ) == Decimal("200.00")

    assert categories[1]["expense_count"] == 1


def test_monthly_analytics_groups_expenses_correctly(
    authenticated_client
):

    expenses = [
        {
            "amount": 100.00,
            "category": "Food",
            "description": "August expense",
            "expense_date": "2026-08-10"
        },
        {
            "amount": 200.00,
            "category": "Food",
            "description": "September expense",
            "expense_date": "2026-09-05"
        },
        {
            "amount": 300.00,
            "category": "Travel",
            "description": "September expense",
            "expense_date": "2026-09-20"
        },
        {
            "amount": 400.00,
            "category": "Shopping",
            "description": "October expense",
            "expense_date": "2026-10-10"
        }
    ]

    for expense in expenses:

        response = authenticated_client.post(
            "/expenses",
            json=expense
        )

        assert response.status_code == 201

    response = authenticated_client.get(
        "/analytics/monthly"
    )

    assert response.status_code == 200

    monthly = response.json()

    assert len(monthly) == 3

    assert monthly[0]["year"] == 2026
    assert monthly[0]["month"] == 8

    assert Decimal(
        str(monthly[0]["total_spending"])
    ) == Decimal("100.00")

    assert monthly[1]["year"] == 2026
    assert monthly[1]["month"] == 9

    assert Decimal(
        str(monthly[1]["total_spending"])
    ) == Decimal("500.00")

    assert monthly[2]["year"] == 2026
    assert monthly[2]["month"] == 10

    assert Decimal(
        str(monthly[2]["total_spending"])
    ) == Decimal("400.00")


def test_spending_trends_calculate_changes(
    authenticated_client
):

    expenses = [
        {
            "amount": 100.00,
            "category": "Food",
            "description": "August",
            "expense_date": "2026-08-10"
        },
        {
            "amount": 200.00,
            "category": "Food",
            "description": "September",
            "expense_date": "2026-09-10"
        },
        {
            "amount": 100.00,
            "category": "Food",
            "description": "October",
            "expense_date": "2026-10-10"
        }
    ]

    for expense in expenses:

        response = authenticated_client.post(
            "/expenses",
            json=expense
        )

        assert response.status_code == 201

    response = authenticated_client.get(
        "/analytics/trends"
    )

    assert response.status_code == 200

    trends = response.json()

    assert len(trends) == 3

    # First month has no previous month

    assert Decimal(
        str(trends[0]["total_spending"])
    ) == Decimal("100.00")

    assert trends[0]["change"] is None

    assert trends[0]["percentage_change"] is None

    # 100 -> 200

    assert Decimal(
        str(trends[1]["total_spending"])
    ) == Decimal("200.00")

    assert Decimal(
        str(trends[1]["change"])
    ) == Decimal("100.00")

    assert Decimal(
        str(trends[1]["percentage_change"])
    ) == Decimal("100.00")

    # 200 -> 100

    assert Decimal(
        str(trends[2]["total_spending"])
    ) == Decimal("100.00")

    assert Decimal(
        str(trends[2]["change"])
    ) == Decimal("-100.00")

    assert Decimal(
        str(trends[2]["percentage_change"])
    ) == Decimal("-50.00")


def test_empty_trends_returns_empty_list(
    authenticated_client
):

    response = authenticated_client.get(
        "/analytics/trends"
    )

    assert response.status_code == 200

    assert response.json() == []


def test_analytics_user_isolation(
    authenticated_client
):

    other_email = (
        "analytics_other_"
        "test@example.com"
    )

    from backend.db import get_db_connection
    from backend.security import hash_password

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
            "Other Analytics User",
            other_email,
            hash_password("TestPassword123")
        )
    )

    other_user_id = cursor.fetchone()[0]

    cursor.execute(
        """
        INSERT INTO expenses (
            user_id,
            amount,
            category,
            description,
            expense_date
        )
        VALUES (%s, %s, %s, %s, %s);
        """,
        (
            other_user_id,
            9999.99,
            "Private",
            "Other user's expense",
            "2026-09-06"
        )
    )

    connection.commit()

    cursor.close()
    connection.close()

    try:

        response = authenticated_client.get(
            "/analytics/summary"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["total_spending"] is None
        assert data["expense_count"] == 0

    finally:

        cleanup_connection = get_db_connection()
        cleanup_cursor = cleanup_connection.cursor()

        cleanup_cursor.execute(
            """
            DELETE FROM expenses
            WHERE user_id = %s;
            """,
            (other_user_id,)
        )

        cleanup_cursor.execute(
            """
            DELETE FROM users
            WHERE id = %s;
            """,
            (other_user_id,)
        )

        cleanup_connection.commit()

        cleanup_cursor.close()
        cleanup_connection.close()