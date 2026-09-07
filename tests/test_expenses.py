def test_create_expense_returns_201(
    authenticated_client
):

    response = authenticated_client.post(
        "/expenses",
        json={
            "amount": 500.00,
            "category": "Food",
            "description": "Lunch",
            "expense_date": "2026-09-06"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["amount"] == "500.00"
    assert data["category"] == "Food"
    assert data["description"] == "Lunch"
    assert data["expense_date"] == "2026-09-06"


def test_get_expenses_returns_200(
    authenticated_client
):

    create_response = authenticated_client.post(
        "/expenses",
        json={
            "amount": 500.00,
            "category": "Food",
            "description": "Lunch",
            "expense_date": "2026-09-06"
        }
    )

    assert create_response.status_code == 201

    response = authenticated_client.get(
        "/expenses"
    )

    assert response.status_code == 200

    expenses = response.json()

    assert len(expenses) == 1
    assert expenses[0]["category"] == "Food"


def test_get_single_expense_returns_200(
    authenticated_client
):

    create_response = authenticated_client.post(
        "/expenses",
        json={
            "amount": 750.00,
            "category": "Travel",
            "description": "Taxi",
            "expense_date": "2026-09-06"
        }
    )

    assert create_response.status_code == 201

    expense_id = create_response.json()["id"]

    response = authenticated_client.get(
        f"/expenses/{expense_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == expense_id
    assert data["category"] == "Travel"
    assert data["amount"] == "750.00"


def test_update_expense_returns_200(
    authenticated_client
):

    create_response = authenticated_client.post(
        "/expenses",
        json={
            "amount": 500.00,
            "category": "Food",
            "description": "Lunch",
            "expense_date": "2026-09-06"
        }
    )

    assert create_response.status_code == 201

    expense_id = create_response.json()["id"]

    response = authenticated_client.put(
        f"/expenses/{expense_id}",
        json={
            "amount": 600.00,
            "category": "Dinner",
            "description": "Dinner",
            "expense_date": "2026-09-06"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == expense_id
    assert data["amount"] == "600.00"
    assert data["category"] == "Dinner"
    assert data["description"] == "Dinner"


def test_delete_expense_returns_204(
    authenticated_client
):

    create_response = authenticated_client.post(
        "/expenses",
        json={
            "amount": 500.00,
            "category": "Food",
            "description": "Lunch",
            "expense_date": "2026-09-06"
        }
    )

    assert create_response.status_code == 201

    expense_id = create_response.json()["id"]

    response = authenticated_client.delete(
        f"/expenses/{expense_id}"
    )

    assert response.status_code == 204


def test_nonexistent_expense_returns_404(
    authenticated_client
):

    response = authenticated_client.get(
        "/expenses/999999999"
    )

    assert response.status_code == 404


def test_expense_requires_authentication(
    client
):

    response = client.get(
        "/expenses"
    )

    assert response.status_code == 401


def test_invalid_expense_returns_422(
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

def test_expense_category_filter(
    authenticated_client
):

    authenticated_client.post(
        "/expenses",
        json={
            "amount": 500.00,
            "category": "Food",
            "description": "Lunch",
            "expense_date": "2026-09-06"
        }
    )

    authenticated_client.post(
        "/expenses",
        json={
            "amount": 1000.00,
            "category": "Travel",
            "description": "Taxi",
            "expense_date": "2026-09-06"
        }
    )

    response = authenticated_client.get(
        "/expenses",
        params={
            "category": "Food"
        }
    )

    assert response.status_code == 200

    expenses = response.json()

    assert len(expenses) == 1
    assert expenses[0]["category"] == "Food"