import streamlit as st

from api import (
    get_budget_comparison,
    get_insights,
    create_budget,
    handle_api_error,
    logout_user
)


def format_amount(value):

    if value is None:
        return "₹0.00"

    return f"₹{float(value):,.2f}"


st.title("💰 Budget Dashboard")


# ============================================================
# Create Budget
# ============================================================

st.subheader("➕ Create Budget")


with st.form("create_budget_form"):

    category = st.text_input("Category")

    amount = st.number_input(
        "Budget Amount",
        min_value=0.01,
        step=100.0
    )

    month = st.number_input(
        "Month",
        min_value=1,
        max_value=12,
        step=1
    )

    year = st.number_input(
        "Year",
        min_value=2020,
        max_value=2100,
        step=1
    )

    submitted = st.form_submit_button("Create Budget")


    if submitted:

        response = create_budget(
            category,
            amount,
            int(month),
            int(year)
        )


        if response is not None and response.status_code == 201:

            st.success(
                "✅ Budget created successfully!"
            )


        elif response is not None and response.status_code == 409:

            st.warning(
                "⚠️ A budget already exists for "
                "this category and month."
            )


        else:

            handle_api_error(
                response,
                "budget"
            )


# ============================================================
# Budget Comparison
# ============================================================

response = get_budget_comparison()


if response is not None and response.status_code == 200:

    budgets = response.json()


    if not budgets:

        st.info(
            "💰 No budgets found."
        )


    else:

        st.subheader(
            "📊 Budget vs Actual"
        )


        for budget in budgets:

            st.write(
                f"### {budget['category']}"
            )


            st.write(
                f"Budget: "
                f"{format_amount(budget['budget_amount'])}"
            )


            st.write(
                f"Spent: "
                f"{format_amount(budget['actual_spending'])}"
            )


            st.write(
                f"Remaining: "
                f"{format_amount(budget['remaining_budget'])}"
            )


            utilization = budget["utilization"]


            if utilization is None:

                st.write(
                    "Used: N/A"
                )

                progress_value = 0.0

            else:

                utilization_value = float(
                    utilization
                )

                st.write(
                    f"Used: "
                    f"{utilization_value:.2f}%"
                )

                progress_value = min(
                    utilization_value / 100,
                    1.0
                )


            st.progress(
                progress_value
            )


            status = budget["status"]


            if status == "Healthy":

                st.success(
                    f"🟢 Status: **{status}**"
                )


            elif status == "Watch":

                st.warning(
                    f"🟡 Status: **{status}**"
                )


            elif status == "Near Limit":

                st.warning(
                    f"🟠 Status: **{status}**"
                )


            elif status == "Over Budget":

                st.error(
                    f"🔴 Status: **{status}**"
                )


            else:

                st.info(
                    f"ℹ️ Status: **{status}**"
                )


            st.divider()


else:

    handle_api_error(
        response,
        "budgets"
    )


# ============================================================
# Financial Insights
# ============================================================

st.subheader("💡 Financial Insights")


insights_response = get_insights()


if (
    insights_response is not None
    and insights_response.status_code == 200
):

    insights = insights_response.json()


    if not insights:

        st.success(
            "✅ You're doing well! "
            "No budget warnings right now."
        )


    else:

        for insight in insights:

            insight_type = insight["type"]

            message = insight["message"]

            severity = insight["severity"]


            title = insight_type.replace(
                "_",
                " "
            ).title()


            if severity == "critical":

                st.error(
                    f"🚨 {title}\n\n"
                    f"{message}"
                )


            elif severity == "warning":

                st.warning(
                    f"⚠️ {title}\n\n"
                    f"{message}"
                )


            else:

                st.info(
                    f"💡 {title}\n\n"
                    f"{message}"
                )


else:

    handle_api_error(
        insights_response,
        "financial insights"
    )