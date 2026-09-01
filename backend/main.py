from fastapi import FastAPI, Depends, status, HTTPException, Query
from decimal import Decimal
from datetime import date

from backend.db import get_db_connection
from backend.schemas import ExpenseCreate, ExpenseResponse

def get_db():
    connection = get_db_connection()

    try:
        yield connection
    finally:
        connection.close()

app = FastAPI(
    title="SmartSpend API",
    description="Personal finance management and analytics API",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "Welcome to SmartSpend API",
        "status": "running"
    }


@app.post(
    "/expenses",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED
)
def create_expense(
    expense: ExpenseCreate,
    connection=Depends(get_db)
):
    cursor = connection.cursor()

    cursor.execute(
    """
    INSERT INTO expenses (
        user_id,
        amount,
        category,
        description,
        expense_date
    )
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id, user_id, amount, category, description, expense_date;
    """,
    (
        expense.user_id,
        expense.amount,
        expense.category,
        expense.description,
        expense.expense_date
    )
)
    created_expense = cursor.fetchone()
    connection.commit()
    cursor.close()
    return {
    "id": created_expense[0],
    "user_id": created_expense[1],
    "amount": created_expense[2],
    "category": created_expense[3],
    "description": created_expense[4],
    "expense_date": created_expense[5]
}

@app.get("/expenses", response_model=list[ExpenseResponse])
def get_expenses(
    user_id: int | None = None,
    category: str | None = None,
    min_amount: Decimal | None = None,
    max_amount: Decimal | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    sort_by: str = "id",
    sort_order: str = "asc",
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    connection=Depends(get_db)
):
    allowed_sort_columns = {
        "id": "id",
        "amount": "amount",
        "expense_date": "expense_date"
    }

    if sort_by not in allowed_sort_columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid sort_by. Allowed values: id, amount, expense_date"
        )

    sort_order = sort_order.lower()

    if sort_order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid sort_order. Allowed values: asc, desc"
        )

    cursor = connection.cursor()

    query = """
        SELECT
            id,
            user_id,
            amount,
            category,
            description,
            expense_date
        FROM expenses
    """

    conditions = []
    values = []

    if user_id is not None:
        conditions.append("user_id = %s")
        values.append(user_id)

    if category:
        conditions.append("category = %s")
        values.append(category)

    if min_amount is not None:
        conditions.append("amount >= %s")
        values.append(min_amount)

    if max_amount is not None:
        conditions.append("amount <= %s")
        values.append(max_amount)

    if start_date is not None:
        conditions.append("expense_date >= %s")
        values.append(start_date)

    if end_date is not None:
        conditions.append("expense_date <= %s")
        values.append(end_date)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    sort_column = allowed_sort_columns[sort_by]

    query += f" ORDER BY {sort_column} {sort_order.upper()}"

    values.extend([limit, offset])

    query += " LIMIT %s OFFSET %s"

    cursor.execute(query, tuple(values))

    expenses = cursor.fetchall()

    cursor.close()

    return [
        {
            "id": expense[0],
            "user_id": expense[1],
            "amount": expense[2],
            "category": expense[3],
            "description": expense[4],
            "expense_date": expense[5]
        }
        for expense in expenses
    ]

@app.get("/expenses/{expense_id}", response_model=ExpenseResponse)
def get_expense(
    expense_id: int,
    connection=Depends(get_db)
):
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            user_id,
            amount,
            category,
            description,
            expense_date
        FROM expenses
        WHERE id = %s;
        """,
        (expense_id,)
    )

    expense = cursor.fetchone()

    cursor.close()

    if expense is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )

    return {
        "id": expense[0],
        "user_id": expense[1],
        "amount": expense[2],
        "category": expense[3],
        "description": expense[4],
        "expense_date": expense[5]
    }

@app.put("/expenses/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: int,
    expense: ExpenseCreate,
    connection=Depends(get_db)
):
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE expenses
        SET
            user_id = %s,
            amount = %s,
            category = %s,
            description = %s,
            expense_date = %s
        WHERE id = %s
        RETURNING
            id,
            user_id,
            amount,
            category,
            description,
            expense_date;
        """,
        (
            expense.user_id,
            expense.amount,
            expense.category,
            expense.description,
            expense.expense_date,
            expense_id
        )
    )

    updated_expense = cursor.fetchone()

    if updated_expense is None:
        cursor.close()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )

    connection.commit()
    cursor.close()

    return {
    "id": updated_expense[0],
    "user_id": updated_expense[1],
    "amount": updated_expense[2],
    "category": updated_expense[3],
    "description": updated_expense[4],
    "expense_date": updated_expense[5]
}

@app.delete(
    "/expenses/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_expense(
    expense_id: int,
    connection=Depends(get_db)
):
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM expenses
        WHERE id = %s;
        """,
        (expense_id,)
    )

    if cursor.rowcount == 0:
        cursor.close()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )

    connection.commit()
    cursor.close()