import streamlit as st

from api import (
    create_expense,
    get_expenses,
    update_expense,
    delete_expense,
    handle_api_error,
    logout_user
)


st.title("My Expenses")


# ============================================================
# Authentication Check
# ============================================================

if "access_token" not in st.session_state:

    st.warning("Please login first.")

    st.stop()
if st.sidebar.button("🚪 Logout"):

    logout_user()

    st.rerun()

# ============================================================
# Add Expense
# ============================================================

st.subheader("Add Expense")


with st.form("expense_form"):

    amount = st.number_input(
        "Amount",
        min_value=0.01,
        step=0.01
    )

    category = st.text_input("Category")

    description = st.text_area("Description")

    expense_date = st.date_input("Expense Date")

    submitted = st.form_submit_button("Add Expense")


if submitted:

    response = create_expense(
        amount,
        category,
        description,
        expense_date.isoformat()
    )

    if response is not None and response.status_code == 201:

        st.success(
            "Expense added successfully!"
        )

    else:

        handle_api_error(
            response,
            "expense"
        )


# ============================================================
# View Expenses
# ============================================================

st.subheader("Expense History")


response = get_expenses()


if response is not None and response.status_code == 200:

    expenses = response.json()

    if expenses:

        expense_table = []

        for expense in expenses:

            expense_table.append({
                "ID": expense["id"],
                "Amount": (
                    f"₹{float(expense['amount']):,.2f}"
                ),
                "Category": expense["category"],
                "Description": (
                    expense["description"]
                    if expense["description"]
                    else "-"
                ),
                "Date": expense["expense_date"]
            })

        st.dataframe(
            expense_table,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No expenses found."
        )


else:

    handle_api_error(
        response,
        "expenses"
    )


# ============================================================
# Update Expense
# ============================================================

st.subheader("Update Expense")


expense_id = st.number_input(
    "Expense ID",
    min_value=1,
    step=1
)


update_amount = st.number_input(
    "New Amount",
    min_value=0.01,
    step=0.01
)


update_category = st.text_input(
    "New Category"
)


update_description = st.text_area(
    "New Description"
)


update_date = st.date_input(
    "New Expense Date"
)


if st.button("Update Expense"):

    response = update_expense(
        int(expense_id),
        update_amount,
        update_category,
        update_description,
        update_date.isoformat()
    )


    if response is not None and response.status_code == 200:

        st.success(
            "Expense updated successfully!"
        )

    else:

        handle_api_error(
            response,
            "expense"
        )


# ============================================================
# Delete Expense
# ============================================================

st.subheader("Delete Expense")


delete_expense_id = st.number_input(
    "Expense ID to Delete",
    min_value=1,
    step=1
)


if st.button("Delete Expense"):

    response = delete_expense(
        int(delete_expense_id)
    )


    if response is not None and response.status_code == 204:

        st.success(
            "Expense deleted successfully!"
        )

    else:

        handle_api_error(
            response,
            "expense"
        )