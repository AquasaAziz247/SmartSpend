from decimal import Decimal


def generate_budget_insight(
    category: str,
    budget_amount: Decimal,
    actual_spending: Decimal,
    utilization: Decimal | None
):
    if utilization is None:
        return None

    if utilization > 100:
        amount_over = actual_spending - budget_amount

        return {
            "type": "over_budget",
            "category": category,
            "message": (
                f"You are ₹{amount_over:.2f} over "
                f"your {category} budget."
            ),
            "severity": "critical"
        }

    if utilization >= 90:
        return {
            "type": "budget_near_limit",
            "category": category,
            "message": (
                f"Your {category} budget is nearly exhausted."
            ),
            "severity": "warning"
        }

    if utilization >= 70:
        return {
            "type": "budget_warning",
            "category": category,
            "message": (
                f"You're approaching your {category} budget limit."
            ),
            "severity": "warning"
        }

    return None

def generate_financial_insights(budget_comparisons):
    insights = []

    for budget in budget_comparisons:

        insight = generate_budget_insight(
            budget.category,
            budget.budget_amount,
            budget.actual_spending,
            budget.utilization
        )

        if insight:
            insights.append(insight)

    return insights