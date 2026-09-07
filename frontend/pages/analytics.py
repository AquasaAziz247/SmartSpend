import streamlit as st

from api import (
    authenticated_request,
    handle_api_error,
    logout_user
)


# ============================================================
# Helper Functions
# ============================================================

def format_amount(value):

    if value is None:
        value = 0

    return f"₹{float(value):,.2f}"


def format_percentage(value):

    if value is None:
        return "N/A"

    return f"{float(value):.2f}%"


# ============================================================
# Page Header
# ============================================================

st.title("SmartSpend")
st.caption("Financial Dashboard")


# ============================================================
# Authentication
# ============================================================

if "access_token" not in st.session_state:

    st.warning("Please login first.")

    st.stop()


# ============================================================
# Logout
# ============================================================

if st.sidebar.button("🚪 Logout"):

    logout_user()

    st.rerun()


# ============================================================
# Fetch Analytics Data
# ============================================================

summary_response = authenticated_request(
    "GET",
    "/analytics/summary"
)

category_response = authenticated_request(
    "GET",
    "/analytics/categories"
)

monthly_response = authenticated_request(
    "GET",
    "/analytics/monthly"
)

trend_response = authenticated_request(
    "GET",
    "/analytics/trends"
)


summary = None
categories = None
monthly_data = None
trends = None


# ============================================================
# Handle Analytics Responses
# ============================================================

if summary_response is not None and summary_response.status_code == 200:

    summary = summary_response.json()

else:

    handle_api_error(
        summary_response,
        "summary"
    )


if category_response is not None and category_response.status_code == 200:

    categories = category_response.json()

else:

    handle_api_error(
        category_response,
        "category data"
    )


if monthly_response is not None and monthly_response.status_code == 200:

    monthly_data = monthly_response.json()

else:

    handle_api_error(
        monthly_response,
        "monthly data"
    )


if trend_response is not None and trend_response.status_code == 200:

    trends = trend_response.json()

else:

    handle_api_error(
        trend_response,
        "spending trends"
    )


# ============================================================
# Overview
# ============================================================

st.subheader("Overview")


if summary is not None:

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Total Spending",
            format_amount(
                summary["total_spending"]
            )
        )

    with col2:

        st.metric(
            "Number of Expenses",
            summary["expense_count"]
        )

    with col3:

        st.metric(
            "Average Expense",
            format_amount(
                summary["average_expense"]
            )
        )


# ============================================================
# Additional Insights
# ============================================================

if summary is not None:

    st.subheader("Additional Insights")

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Highest Expense",
            format_amount(
                summary["highest_expense"]
            )
        )

    with col2:

        st.metric(
            "Lowest Expense",
            format_amount(
                summary["lowest_expense"]
            )
        )


# ============================================================
# Spending Analysis
# ============================================================

st.subheader("Spending Analysis")


# ============================================================
# Category + Monthly Charts
# ============================================================

if categories and monthly_data:

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # Category Comparison
    # --------------------------------------------------------

    with col1:

        st.write("#### Category Comparison")

        category_chart = {
            "Category": [
                item["category"]
                for item in categories
            ],
            "Spending": [
                float(item["total_spending"])
                for item in categories
            ]
        }

        st.bar_chart(
            category_chart,
            x="Category",
            y="Spending"
        )

    # --------------------------------------------------------
    # Monthly Spending Trend
    # --------------------------------------------------------

    with col2:

        st.write("#### Monthly Spending Trend")

        monthly_chart = {
            "Month": [
                f"{item['year']}-{item['month']:02d}"
                for item in monthly_data
            ],
            "Spending": [
                float(item["total_spending"])
                for item in monthly_data
            ]
        }

        st.line_chart(
            monthly_chart,
            x="Month",
            y="Spending"
        )


elif not categories and not monthly_data:

    st.info(
        "No spending analysis data available."
    )


# ============================================================
# Category Details
# ============================================================

if categories:

    st.subheader("Category Details")

    category_table = []

    for item in categories:

        category_table.append({
            "Category": item["category"],
            "Total Spending": format_amount(
                item["total_spending"]
            ),
            "Number of Expenses": item["expense_count"]
        })

    st.dataframe(
        category_table,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# Monthly Details
# ============================================================

if monthly_data:

    st.subheader("Monthly Details")

    monthly_table = []

    for item in monthly_data:

        month_number = item["month"]

        month_names = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December"
        ]

        month_name = month_names[month_number - 1]

        monthly_table.append({
            "Month": (
                f"{month_name} {item['year']}"
            ),
            "Total Spending": format_amount(
                item["total_spending"]
            )
        })

    st.dataframe(
        monthly_table,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# Spending Trends
# ============================================================

st.subheader("Spending Trends")


if trends:

    # --------------------------------------------------------
    # Latest Trend
    # --------------------------------------------------------

    latest_trend = trends[-1]

    latest_spending = latest_trend[
        "total_spending"
    ]

    latest_change = latest_trend[
        "change"
    ]

    latest_percentage = latest_trend[
        "percentage_change"
    ]


    # --------------------------------------------------------
    # Trend Metrics
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Latest Month Spending",
            format_amount(
                latest_spending
            )
        )

    with col2:

        if latest_change is not None:

            st.metric(
                "Monthly Change",
                format_amount(
                    latest_change
                )
            )

        else:

            st.metric(
                "Monthly Change",
                "N/A"
            )

    with col3:

        st.metric(
            "Percentage Change",
            format_percentage(
                latest_percentage
            )
        )


    # --------------------------------------------------------
    # Detailed Trend Data
    # --------------------------------------------------------

    with st.expander(
        "View Detailed Trend Data"
    ):

        trend_table = []

        for item in trends:

            trend_table.append({
                "Year": item["year"],
                "Month": item["month"],
                "Total Spending": format_amount(
                    item["total_spending"]
                ),
                "Change": (
                    format_amount(item["change"])
                    if item["change"] is not None
                    else "N/A"
                ),
                "Percentage Change": (
                    format_percentage(
                        item["percentage_change"]
                    )
                    if item["percentage_change"] is not None
                    else "N/A"
                )
            })

        st.dataframe(
            trend_table,
            use_container_width=True,
            hide_index=True
        )


    # --------------------------------------------------------
    # Spending Trend Chart
    # --------------------------------------------------------

    st.write("#### Spending Trend")

    trend_chart = {
        "Month": [
            f"{item['year']}-{item['month']:02d}"
            for item in trends
        ],
        "Spending": [
            float(item["total_spending"])
            for item in trends
        ]
    }

    st.line_chart(
        trend_chart,
        x="Month",
        y="Spending"
    )


else:

    st.info(
        "No spending trend data available."
    )