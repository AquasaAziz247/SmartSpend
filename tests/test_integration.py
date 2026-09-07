import uuid

from backend.db import get_db_connection


def test_complete_budget_insight_user_flow(
    client
):

    email = (
        f"integration_{uuid.uuid4().hex}"
        "@example.com"
    )

    try:

        # ============================================
        # 1. Register
        # ============================================

        register_response = client.post(
            "/users/register",
            json={
                "name": "Integration Test User",
                "email": email,
                "password": "TestPassword123"
            }
        )

        assert register_response.status_code == 201


        # ============================================
        # 2. Login
        # ============================================

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


        # ============================================
        # 3. Create Expense
        # ============================================

        expense_response = client.post(
            "/expenses",
            headers=headers,
            json={
                "amount": 150.00,
                "category": "Food",
                "description": "Integration test expense",
                "expense_date": "2026-09-06"
            }
        )

        assert expense_response.status_code == 201

        expense_id = expense_response.json()["id"]


        # ============================================
        # 4. Create Budget
        # ============================================

        budget_response = client.post(
            "/budgets",
            headers=headers,
            json={
                "category": "Food",
                "amount": 100.00,
                "month": 9,
                "year": 2026
            }
        )

        assert budget_response.status_code == 201

        budget_id = budget_response.json()["id"]


        # ============================================
        # 5. Budget Comparison
        # ============================================

        comparison_response = client.get(
            "/budgets/comparison",
            headers=headers
        )

        assert comparison_response.status_code == 200

        comparisons = comparison_response.json()

        food_budget = next(
            budget
            for budget in comparisons
            if budget["id"] == budget_id
        )

        assert food_budget["category"] == "Food"
        assert food_budget["budget_amount"] == "100.00"
        assert food_budget["actual_spending"] == "150.00"
        assert food_budget["remaining_budget"] == "-50.00"
        assert food_budget["status"] == "Over Budget"


        # ============================================
        # 6. Financial Insights
        # ============================================

        insights_response = client.get(
            "/insights",
            headers=headers
        )

        assert insights_response.status_code == 200

        insights = insights_response.json()

        assert len(insights) == 1

        insight = insights[0]

        assert insight["type"] == "over_budget"
        assert insight["category"] == "Food"
        assert insight["severity"] == "critical"

        assert (
            insight["message"]
            == "You are ₹50.00 over your Food budget."
        )


        # ============================================
        # 7. Cleanup test data
        # ============================================

        delete_expense_response = client.delete(
            f"/expenses/{expense_id}",
            headers=headers
        )

        assert delete_expense_response.status_code == 204


        delete_budget_response = client.delete(
            f"/budgets/{budget_id}",
            headers=headers
        )

        assert delete_budget_response.status_code == 204


    finally:

        connection = get_db_connection()
        cursor = connection.cursor()

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