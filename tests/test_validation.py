def test_negative_expense_amount_returns_422(
    authenticated_client
):

    response = authenticated_client.post(
        "/expenses",
        json={
            "amount": -100.00,
            "category": "Food",
            "description": "Invalid expense",
            "expense_date": "2026-09-06"
        }
    )

    assert response.status_code == 422


def test_zero_expense_amount_returns_422(
    authenticated_client
):

    response = authenticated_client.post(
        "/expenses",
        json={
            "amount": 0,
            "category": "Food",
            "description": "Invalid expense",
            "expense_date": "2026-09-06"
        }
    )

    assert response.status_code == 422


def test_empty_expense_category_returns_422(
    authenticated_client
):

    response = authenticated_client.post(
        "/expenses",
        json={
            "amount": 100.00,
            "category": "",
            "description": "Invalid category",
            "expense_date": "2026-09-06"
        }
    )

    assert response.status_code == 422


def test_oversized_expense_category_returns_422(
    authenticated_client
):

    oversized_category = "A" * 51

    response = authenticated_client.post(
        "/expenses",
        json={
            "amount": 100.00,
            "category": oversized_category,
            "description": "Invalid category",
            "expense_date": "2026-09-06"
        }
    )

    assert response.status_code == 422


def test_invalid_expense_date_returns_422(
    authenticated_client
):

    response = authenticated_client.post(
        "/expenses",
        json={
            "amount": 100.00,
            "category": "Food",
            "description": "Invalid date",
            "expense_date": "not-a-date"
        }
    )

    assert response.status_code == 422


def test_missing_expense_amount_returns_422(
    authenticated_client
):

    response = authenticated_client.post(
        "/expenses",
        json={
            "category": "Food",
            "description": "Missing amount",
            "expense_date": "2026-09-06"
        }
    )

    assert response.status_code == 422


def test_missing_expense_category_returns_422(
    authenticated_client
):

    response = authenticated_client.post(
        "/expenses",
        json={
            "amount": 100.00,
            "description": "Missing category",
            "expense_date": "2026-09-06"
        }
    )

    assert response.status_code == 422


def test_missing_expense_date_returns_422(
    authenticated_client
):

    response = authenticated_client.post(
        "/expenses",
        json={
            "amount": 100.00,
            "category": "Food",
            "description": "Missing date"
        }
    )

    assert response.status_code == 422

def test_negative_budget_amount_returns_422(
    authenticated_client
):

    response = authenticated_client.post(
        "/budgets",
        json={
            "category": "Food",
            "amount": -100.00,
            "month": 9,
            "year": 2026
        }
    )

    assert response.status_code == 422


def test_zero_budget_amount_returns_422(
    authenticated_client
):

    response = authenticated_client.post(
        "/budgets",
        json={
            "category": "Food",
            "amount": 0,
            "month": 9,
            "year": 2026
        }
    )

    assert response.status_code == 422


def test_budget_month_zero_returns_422(
    authenticated_client
):

    response = authenticated_client.post(
        "/budgets",
        json={
            "category": "Food",
            "amount": 1000.00,
            "month": 0,
            "year": 2026
        }
    )

    assert response.status_code == 422


def test_budget_month_thirteen_returns_422(
    authenticated_client
):

    response = authenticated_client.post(
        "/budgets",
        json={
            "category": "Food",
            "amount": 1000.00,
            "month": 13,
            "year": 2026
        }
    )

    assert response.status_code == 422


def test_empty_budget_category_returns_422(
    authenticated_client
):

    response = authenticated_client.post(
        "/budgets",
        json={
            "category": "",
            "amount": 1000.00,
            "month": 9,
            "year": 2026
        }
    )

    assert response.status_code == 422


def test_oversized_budget_category_returns_422(
    authenticated_client
):

    oversized_category = "A" * 51

    response = authenticated_client.post(
        "/budgets",
        json={
            "category": oversized_category,
            "amount": 1000.00,
            "month": 9,
            "year": 2026
        }
    )

    assert response.status_code == 422

def test_get_nonexistent_expense_returns_404(
    authenticated_client
):

    response = authenticated_client.get(
        "/expenses/999999999"
    )

    assert response.status_code == 404


def test_update_nonexistent_expense_returns_404(
    authenticated_client
):

    response = authenticated_client.put(
        "/expenses/999999999",
        json={
            "amount": 100.00,
            "category": "Food",
            "description": "Nonexistent expense",
            "expense_date": "2026-09-06"
        }
    )

    assert response.status_code == 404


def test_delete_nonexistent_expense_returns_404(
    authenticated_client
):

    response = authenticated_client.delete(
        "/expenses/999999999"
    )

    assert response.status_code == 404


def test_update_nonexistent_budget_returns_404(
    authenticated_client
):

    response = authenticated_client.put(
        "/budgets/999999999",
        json={
            "category": "Food",
            "amount": 1000.00,
            "month": 9,
            "year": 2026
        }
    )

    assert response.status_code == 404


def test_delete_nonexistent_budget_returns_404(
    authenticated_client
):

    response = authenticated_client.delete(
        "/budgets/999999999"
    )

    assert response.status_code == 404


def test_missing_token_returns_401(
    client
):

    response = client.get(
        "/expenses"
    )

    assert response.status_code == 401


def test_invalid_token_returns_401(
    client
):

    response = client.get(
        "/expenses",
        headers={
            "Authorization": "Bearer invalid.token.value"
        }
    )

    assert response.status_code == 401