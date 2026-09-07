from decimal import Decimal

from backend.main import build_budget_comparisons


def test_zero_spending_has_zero_utilization():

    results = build_budget_comparisons([
        (
            1,
            1,
            "Food",
            Decimal("5000.00"),
            Decimal("0.00"),
            9,
            2026
        )
    ])

    comparison = results[0]

    assert comparison.utilization == Decimal("0.00")
    assert comparison.remaining_budget == Decimal("5000.00")
    assert comparison.status == "Healthy"


def test_70_percent_utilization_is_watch():

    results = build_budget_comparisons([
        (
            2,
            1,
            "Food",
            Decimal("5000.00"),
            Decimal("3500.00"),
            9,
            2026
        )
    ])

    comparison = results[0]

    assert comparison.utilization == Decimal("70.00")
    assert comparison.remaining_budget == Decimal("1500.00")
    assert comparison.status == "Watch"


def test_90_percent_utilization_is_near_limit():

    results = build_budget_comparisons([
        (
            3,
            1,
            "Food",
            Decimal("5000.00"),
            Decimal("4500.00"),
            9,
            2026
        )
    ])

    comparison = results[0]

    assert comparison.utilization == Decimal("90.00")
    assert comparison.remaining_budget == Decimal("500.00")
    assert comparison.status == "Near Limit"


def test_100_percent_utilization_is_near_limit():

    results = build_budget_comparisons([
        (
            4,
            1,
            "Food",
            Decimal("5000.00"),
            Decimal("5000.00"),
            9,
            2026
        )
    ])

    comparison = results[0]

    assert comparison.utilization == Decimal("100.00")
    assert comparison.remaining_budget == Decimal("0.00")
    assert comparison.status == "Near Limit"


def test_over_budget_is_detected():

    results = build_budget_comparisons([
        (
            5,
            1,
            "Food",
            Decimal("5000.00"),
            Decimal("5500.00"),
            9,
            2026
        )
    ])

    comparison = results[0]

    assert comparison.utilization == Decimal("110.00")
    assert comparison.remaining_budget == Decimal("-500.00")
    assert comparison.status == "Over Budget"


def test_decimal_precision_is_preserved():

    results = build_budget_comparisons([
        (
            6,
            1,
            "Travel",
            Decimal("3000.00"),
            Decimal("1234.56"),
            9,
            2026
        )
    ])

    comparison = results[0]

    assert comparison.remaining_budget == Decimal("1765.44")
    assert comparison.utilization == (
        Decimal("41.152")
    )
    assert comparison.status == "Healthy"


def test_zero_budget_is_handled_defensively():

    results = build_budget_comparisons([
        (
            7,
            1,
            "Emergency",
            Decimal("0.00"),
            Decimal("0.00"),
            9,
            2026
        )
    ])

    comparison = results[0]

    assert comparison.utilization is None
    assert comparison.remaining_budget == Decimal("0.00")
    assert comparison.status == "Not Set"

def test_create_budget_returns_201(
    authenticated_client
):

    response = authenticated_client.post(
        "/budgets",
        json={
            "category": "Food",
            "amount": 5000.00,
            "month": 9,
            "year": 2026
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["category"] == "Food"
    assert data["amount"] == "5000.00"
    assert data["month"] == 9
    assert data["year"] == 2026


def test_get_budgets_returns_200(
    authenticated_client
):

    create_response = authenticated_client.post(
        "/budgets",
        json={
            "category": "Food",
            "amount": 5000.00,
            "month": 9,
            "year": 2026
        }
    )

    assert create_response.status_code == 201

    response = authenticated_client.get(
        "/budgets"
    )

    assert response.status_code == 200

    budgets = response.json()

    assert len(budgets) == 1
    assert budgets[0]["category"] == "Food"
    assert budgets[0]["amount"] == "5000.00"


def test_update_budget_returns_200(
    authenticated_client
):

    create_response = authenticated_client.post(
        "/budgets",
        json={
            "category": "Food",
            "amount": 5000.00,
            "month": 9,
            "year": 2026
        }
    )

    assert create_response.status_code == 201

    budget_id = create_response.json()["id"]

    response = authenticated_client.put(
        f"/budgets/{budget_id}",
        json={
            "category": "Food",
            "amount": 6000.00,
            "month": 9,
            "year": 2026
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == budget_id
    assert data["category"] == "Food"
    assert data["amount"] == "6000.00"


def test_delete_budget_returns_204(
    authenticated_client
):

    create_response = authenticated_client.post(
        "/budgets",
        json={
            "category": "Travel",
            "amount": 3000.00,
            "month": 9,
            "year": 2026
        }
    )

    assert create_response.status_code == 201

    budget_id = create_response.json()["id"]

    response = authenticated_client.delete(
        f"/budgets/{budget_id}"
    )

    assert response.status_code == 204


def test_duplicate_budget_returns_409(
    authenticated_client
):

    budget = {
        "category": "Food",
        "amount": 5000.00,
        "month": 9,
        "year": 2026
    }

    first_response = authenticated_client.post(
        "/budgets",
        json=budget
    )

    assert first_response.status_code == 201

    second_response = authenticated_client.post(
        "/budgets",
        json=budget
    )

    assert second_response.status_code == 409


def test_nonexistent_budget_returns_404(
    authenticated_client
):

    response = authenticated_client.delete(
        "/budgets/999999999"
    )

    assert response.status_code == 404


def test_budget_requires_authentication(client):

    response = client.get(
        "/budgets"
    )

    assert response.status_code == 401


def test_invalid_budget_returns_422(
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