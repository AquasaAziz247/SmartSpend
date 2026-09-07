from decimal import Decimal

from backend.insights import generate_budget_insight


def test_healthy_budget_returns_no_insight():

    result = generate_budget_insight(
        category="Food",
        budget_amount=Decimal("5000.00"),
        actual_spending=Decimal("2000.00"),
        utilization=Decimal("40.00")
    )

    assert result is None


def test_70_percent_utilization_returns_warning():

    result = generate_budget_insight(
        category="Food",
        budget_amount=Decimal("5000.00"),
        actual_spending=Decimal("3500.00"),
        utilization=Decimal("70.00")
    )

    assert result is not None
    assert result["type"] == "budget_warning"
    assert result["category"] == "Food"
    assert result["severity"] == "warning"


def test_89_99_percent_utilization_returns_warning():

    result = generate_budget_insight(
        category="Food",
        budget_amount=Decimal("5000.00"),
        actual_spending=Decimal("4499.50"),
        utilization=Decimal("89.99")
    )

    assert result is not None
    assert result["type"] == "budget_warning"
    assert result["severity"] == "warning"


def test_90_percent_utilization_returns_near_limit():

    result = generate_budget_insight(
        category="Food",
        budget_amount=Decimal("5000.00"),
        actual_spending=Decimal("4500.00"),
        utilization=Decimal("90.00")
    )

    assert result is not None
    assert result["type"] == "budget_near_limit"
    assert result["category"] == "Food"
    assert result["severity"] == "warning"


def test_100_percent_utilization_returns_near_limit():

    result = generate_budget_insight(
        category="Food",
        budget_amount=Decimal("5000.00"),
        actual_spending=Decimal("5000.00"),
        utilization=Decimal("100.00")
    )

    assert result is not None
    assert result["type"] == "budget_near_limit"
    assert result["severity"] == "warning"


def test_over_100_percent_utilization_returns_over_budget():

    result = generate_budget_insight(
        category="Food",
        budget_amount=Decimal("5000.00"),
        actual_spending=Decimal("5500.00"),
        utilization=Decimal("110.00")
    )

    assert result is not None
    assert result["type"] == "over_budget"
    assert result["category"] == "Food"
    assert result["severity"] == "critical"


def test_over_budget_message_contains_amount_and_category():

    result = generate_budget_insight(
        category="Travel",
        budget_amount=Decimal("3000.00"),
        actual_spending=Decimal("3500.00"),
        utilization=Decimal("116.67")
    )

    assert result is not None
    assert result["message"] == (
        "You are ₹500.00 over your Travel budget."
    )


def test_none_utilization_returns_no_insight():

    result = generate_budget_insight(
        category="Food",
        budget_amount=Decimal("5000.00"),
        actual_spending=Decimal("2000.00"),
        utilization=None
    )

    assert result is None