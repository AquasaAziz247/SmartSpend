from db import get_db_connection


connection = get_db_connection()
cursor = connection.cursor()


# -----------------------------
# 1. Create a user
# -----------------------------

insert_user_query = """
    INSERT INTO users (name, email, password_hash)
    VALUES (%s, %s, %s)
    RETURNING id;
"""

cursor.execute(
    insert_user_query,
    ("Bob", "bob@example.com", "temporary_hash")
)

user_id = cursor.fetchone()[0]

connection.commit()

print(f"User created successfully! ID: {user_id}")


# -----------------------------
# 2. Create an expense
# -----------------------------

insert_expense_query = """
    INSERT INTO expenses
        (user_id, amount, category, description, expense_date)
    VALUES
        (%s, %s, %s, %s, %s)
    RETURNING id;
"""

cursor.execute(
    insert_expense_query,
    (
        user_id,
        500.00,
        "Food",
        "Dinner",
        "2026-08-31"
    )
)

expense_id = cursor.fetchone()[0]

connection.commit()

print(f"Expense created successfully! ID: {expense_id}")


# -----------------------------
# 3. Retrieve the expense
# -----------------------------

select_query = """
    SELECT id, user_id, amount, category, description, expense_date
    FROM expenses
    WHERE id = %s;
"""

cursor.execute(select_query, (expense_id,))

expense = cursor.fetchone()

print("\nExpense retrieved successfully:")
print(expense)


cursor.close()
connection.close()