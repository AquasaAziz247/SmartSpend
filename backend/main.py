from fastapi import FastAPI, Depends, status, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from decimal import Decimal
from datetime import date
from backend.insights import generate_financial_insights

from backend.db import get_db_connection

from backend.schemas import (
    ExpenseCreate,
    ExpenseResponse,
    UserRegister,
    UserResponse,
    TokenResponse,
    ExpenseSummary,
    CategorySummary,
    MonthlySummary,
    SpendingTrend,
    BudgetCreate,
    BudgetUpdate,
    BudgetResponse,
    BudgetComparison,
    FinancialInsight
)

from backend.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)


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

def build_budget_comparisons(results):
    comparisons = []

    for row in results:
        budget_amount = row[3]
        actual_spending = row[4]

        if budget_amount > 0:
            utilization = (
                actual_spending / budget_amount
            ) * 100
        else:
            utilization = None

        remaining_budget = (
            budget_amount - actual_spending
        )

        if utilization is None:
            budget_status = "Not Set"
        elif utilization < 70:
            budget_status = "Healthy"
        elif utilization < 90:
            budget_status = "Watch"
        elif utilization <= 100:
            budget_status = "Near Limit"
        else:
            budget_status = "Over Budget"

        comparisons.append(
            BudgetComparison(
                id=row[0],
                user_id=row[1],
                category=row[2],
                budget_amount=budget_amount,
                actual_spending=actual_spending,
                utilization=utilization,
                remaining_budget=remaining_budget,
                status=budget_status,
                month=row[5],
                year=row[6]
            )
        )

    return comparisons


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "Welcome to SmartSpend API",
        "status": "running"
    }


# ============================================================
# USER REGISTRATION
# ============================================================
@app.post(
    "/users/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(
    user: UserRegister,
    connection=Depends(get_db)
):
    cursor = connection.cursor()

    try:

        # Check if email already exists
        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE email = %s;
            """,
            (user.email,)
        )

        existing_user = cursor.fetchone()

        if existing_user is not None:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create user
        cursor.execute(
            """
            INSERT INTO users (
                name,
                email,
                password_hash
            )
            VALUES (%s, %s, %s)
            RETURNING id, name, email;
            """,
            (
                user.name,
                user.email,
                hash_password(user.password)
            )
        )

        created_user = cursor.fetchone()

        connection.commit()

        return {
            "id": created_user[0],
            "name": created_user[1],
            "email": created_user[2]
        }

    except HTTPException:
        connection.rollback()
        raise

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()


# ============================================================
# USER LOGIN
# ============================================================

@app.post(
    "/users/login",
    response_model=TokenResponse
)
def login_user(
    user: OAuth2PasswordRequestForm = Depends(),
    connection=Depends(get_db)
):
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            name,
            email,
            password_hash
        FROM users
        WHERE email = %s;
        """,
        (user.username,)
    )

    existing_user = cursor.fetchone()

    if existing_user is None:
        cursor.close()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    stored_password_hash = existing_user[3]

    if not verify_password(
        user.password,
        stored_password_hash
    ):
        cursor.close()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    cursor.close()

    # Create JWT token
    access_token = create_access_token(
        existing_user[0]
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# ============================================================
# CREATE EXPENSE
# ============================================================

@app.post(
    "/expenses",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED
)
def create_expense(
    expense: ExpenseCreate,
    current_user_id: int = Depends(get_current_user),
    connection=Depends(get_db)
):
    cursor = connection.cursor()

    try:

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
            RETURNING
                id,
                user_id,
                amount,
                category,
                description,
                expense_date;
            """,
            (
                current_user_id,
                expense.amount,
                expense.category,
                expense.description,
                expense.expense_date
            )
        )

        created_expense = cursor.fetchone()

        connection.commit()

        return {
            "id": created_expense[0],
            "user_id": created_expense[1],
            "amount": created_expense[2],
            "category": created_expense[3],
            "description": created_expense[4],
            "expense_date": created_expense[5]
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()


# ============================================================
# GET EXPENSES
# ============================================================

@app.get(
    "/expenses",
    response_model=list[ExpenseResponse]
)
def get_expenses(
    category: str | None = None,
    min_amount: Decimal | None = None,
    max_amount: Decimal | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    sort_by: str = "id",
    sort_order: str = "asc",
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user_id: int = Depends(get_current_user),
    connection=Depends(get_db)
):
    allowed_sort_columns = {
        "id": "id",
        "amount": "amount",
        "expense_date": "expense_date"
    }

    # Validate sort column
    if sort_by not in allowed_sort_columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Invalid sort_by. "
                "Allowed values: id, amount, expense_date"
            )
        )

    # Validate sort order
    sort_order = sort_order.lower()

    if sort_order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Invalid sort_order. "
                "Allowed values: asc, desc"
            )
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

    # Always restrict results to logged-in user
    conditions.append("user_id = %s")
    values.append(current_user_id)

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

    query += " WHERE " + " AND ".join(conditions)

    sort_column = allowed_sort_columns[sort_by]

    query += (
        f" ORDER BY {sort_column} "
        f"{sort_order.upper()}"
    )

    values.extend([limit, offset])

    query += " LIMIT %s OFFSET %s"

    cursor.execute(
        query,
        tuple(values)
    )

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


# ============================================================
# GET SINGLE EXPENSE
# ============================================================

@app.get(
    "/expenses/{expense_id}",
    response_model=ExpenseResponse
)
def get_expense(
    expense_id: int,
    current_user_id: int = Depends(get_current_user),
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
        WHERE id = %s
        AND user_id = %s;
        """,
        (
            expense_id,
            current_user_id
        )
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


# ============================================================
# UPDATE EXPENSE
# ============================================================

@app.put(
    "/expenses/{expense_id}",
    response_model=ExpenseResponse
)
def update_expense(
    expense_id: int,
    expense: ExpenseCreate,
    current_user_id: int = Depends(get_current_user),
    connection=Depends(get_db)
):
    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            UPDATE expenses
            SET
                amount = %s,
                category = %s,
                description = %s,
                expense_date = %s
            WHERE id = %s
            AND user_id = %s
            RETURNING
                id,
                user_id,
                amount,
                category,
                description,
                expense_date;
            """,
            (
                expense.amount,
                expense.category,
                expense.description,
                expense.expense_date,
                expense_id,
                current_user_id
            )
        )

        updated_expense = cursor.fetchone()

        if updated_expense is None:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found"
            )

        connection.commit()

        return {
            "id": updated_expense[0],
            "user_id": updated_expense[1],
            "amount": updated_expense[2],
            "category": updated_expense[3],
            "description": updated_expense[4],
            "expense_date": updated_expense[5]
        }

    except HTTPException:
        connection.rollback()
        raise

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()

# ============================================================
# DELETE EXPENSE
# ============================================================

@app.delete(
    "/expenses/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_expense(
    expense_id: int,
    current_user_id: int = Depends(get_current_user),
    connection=Depends(get_db)
):
    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM expenses
            WHERE id = %s
            AND user_id = %s;
            """,
            (
                expense_id,
                current_user_id
            )
        )

        if cursor.rowcount == 0:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found"
            )

        connection.commit()

    except HTTPException:

        connection.rollback()
        raise

    except Exception:

        connection.rollback()
        raise

    finally:

        cursor.close()

# ============================================================
# EXPENSE ANALYTICS SUMMARY
# ============================================================

@app.get(
    "/analytics/summary",
    response_model=ExpenseSummary
)
def get_expense_summary(
    current_user_id: int = Depends(get_current_user),
    connection=Depends(get_db)
):
    cursor = connection.cursor()

    query = """
        SELECT
            SUM(amount) AS total_spending,
            COUNT(*) AS expense_count,
            AVG(amount) AS average_expense,
            MAX(amount) AS highest_expense,
            MIN(amount) AS lowest_expense
        FROM expenses
        WHERE user_id = %s;
    """

    cursor.execute(
        query,
        (current_user_id,)
    )

    summary = cursor.fetchone()

    cursor.close()

    return {
        "total_spending": summary[0],
        "expense_count": summary[1],
        "average_expense": summary[2],
        "highest_expense": summary[3],
        "lowest_expense": summary[4]
    }

# ============================================================
# CATEGORY-WISE EXPENSE ANALYTICS
# ============================================================

@app.get(
    "/analytics/categories",
    response_model=list[CategorySummary]
)
def get_category_summary(
    current_user_id: int = Depends(get_current_user),
    connection=Depends(get_db)
):
    cursor = connection.cursor()

    query = """
        SELECT
            category,
            SUM(amount) AS total_spending,
            COUNT(*) AS expense_count
        FROM expenses
        WHERE user_id = %s
        GROUP BY category
        ORDER BY total_spending DESC;
    """

    cursor.execute(
        query,
        (current_user_id,)
    )

    results = cursor.fetchall()

    cursor.close()

    return [
        {
            "category": row[0],
            "total_spending": row[1],
            "expense_count": row[2]
        }
        for row in results
    ]

# ============================================================
# MONTHLY SPENDING ANALYTICS
# ============================================================

@app.get(
    "/analytics/monthly",
    response_model=list[MonthlySummary]
)
def get_monthly_summary(
    current_user_id: int = Depends(get_current_user),
    connection=Depends(get_db)
):
    cursor = connection.cursor()

    query = """
        SELECT
            EXTRACT(YEAR FROM expense_date) AS year,
            EXTRACT(MONTH FROM expense_date) AS month,
            SUM(amount) AS total_spending
        FROM expenses
        WHERE user_id = %s
        GROUP BY
            EXTRACT(YEAR FROM expense_date),
            EXTRACT(MONTH FROM expense_date)
        ORDER BY
            EXTRACT(YEAR FROM expense_date),
            EXTRACT(MONTH FROM expense_date);
    """

    cursor.execute(
        query,
        (current_user_id,)
    )

    results = cursor.fetchall()

    cursor.close()

    return [
        {
            "year": int(row[0]),
            "month": int(row[1]),
            "total_spending": row[2]
        }
        for row in results
    ]

# ============================================================
# SPENDING TRENDS
# ============================================================

@app.get(
    "/analytics/trends",
    response_model=list[SpendingTrend]
)
def get_spending_trends(
    current_user_id: int = Depends(get_current_user),
    connection=Depends(get_db)
):

    cursor = connection.cursor()

    query = """
        SELECT
            EXTRACT(YEAR FROM expense_date)::int AS year,
            EXTRACT(MONTH FROM expense_date)::int AS month,
            SUM(amount) AS total_spending
        FROM expenses
        WHERE user_id = %s
        GROUP BY
            EXTRACT(YEAR FROM expense_date),
            EXTRACT(MONTH FROM expense_date)
        ORDER BY
            EXTRACT(YEAR FROM expense_date),
            EXTRACT(MONTH FROM expense_date);
    """

    cursor.execute(
        query,
        (current_user_id,)
    )

    results = cursor.fetchall()

    cursor.close()

    previous_spending = None

    trends = []

    for row in results:

        current_spending = row[2]

        if previous_spending is None:
           change = None
           percentage_change = None

        elif previous_spending == 0:
             change = current_spending - previous_spending
             percentage_change = None

        else:
             change = current_spending - previous_spending
             percentage_change = (
                 (change / previous_spending) * 100
           )

        trends.append({
            "year": row[0],
            "month": row[1],
            "total_spending": current_spending,
            "change": change,
            "percentage_change": percentage_change
        })

        previous_spending = current_spending

    return trends

# ============================================================
# CREATE BUDGET
# ============================================================

@app.post(
    "/budgets",
    response_model=BudgetResponse,
    status_code=status.HTTP_201_CREATED
)
def create_budget(
    budget: BudgetCreate,
    current_user_id: int = Depends(get_current_user),
    connection=Depends(get_db)
):
    cursor = connection.cursor()

    try:

        # Check if budget already exists
        cursor.execute(
            """
            SELECT id
            FROM budgets
            WHERE user_id = %s
              AND category = %s
              AND month = %s
              AND year = %s;
            """,
            (
                current_user_id,
                budget.category,
                budget.month,
                budget.year
            )
        )

        existing_budget = cursor.fetchone()

        if existing_budget is not None:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Budget already exists for "
                    "this category and month"
                )
            )

        # Create budget
        cursor.execute(
            """
            INSERT INTO budgets (
                user_id,
                category,
                amount,
                month,
                year
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING
                id,
                user_id,
                category,
                amount,
                month,
                year,
                created_at;
            """,
            (
                current_user_id,
                budget.category,
                budget.amount,
                budget.month,
                budget.year
            )
        )

        created_budget = cursor.fetchone()

        connection.commit()

        return {
            "id": created_budget[0],
            "user_id": created_budget[1],
            "category": created_budget[2],
            "amount": created_budget[3],
            "month": created_budget[4],
            "year": created_budget[5],
            "created_at": created_budget[6]
        }

    except HTTPException:

        connection.rollback()
        raise

    except Exception:

        connection.rollback()
        raise

    finally:

        cursor.close()


# ============================================================
# GET BUDGETS
# ============================================================

@app.get(
    "/budgets",
    response_model=list[BudgetResponse]
)
def get_budgets(
    current_user_id: int = Depends(get_current_user),
    connection=Depends(get_db)
):
    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            SELECT
                id,
                user_id,
                category,
                amount,
                month,
                year,
                created_at
            FROM budgets
            WHERE user_id = %s
            ORDER BY
                year DESC,
                month DESC;
            """,
            (current_user_id,)
        )

        budgets = cursor.fetchall()

        return [
            {
                "id": budget[0],
                "user_id": budget[1],
                "category": budget[2],
                "amount": budget[3],
                "month": budget[4],
                "year": budget[5],
                "created_at": budget[6]
            }
            for budget in budgets
        ]

    finally:

        cursor.close()

# ============================================================
# UPDATE BUDGET
# ============================================================

@app.put(
    "/budgets/{budget_id}",
    response_model=BudgetResponse
)
def update_budget(
    budget_id: int,
    budget: BudgetUpdate,
    current_user_id: int = Depends(get_current_user),
    connection=Depends(get_db)
):
    cursor = connection.cursor()

    try:

        # Check whether the budget belongs to the logged-in user
        cursor.execute(
            """
            SELECT id
            FROM budgets
            WHERE id = %s
            AND user_id = %s;
            """,
            (
                budget_id,
                current_user_id
            )
        )

        existing_budget = cursor.fetchone()

        if existing_budget is None:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Budget not found"
            )

        # Check for duplicate category/month/year
        cursor.execute(
            """
            SELECT id
            FROM budgets
            WHERE user_id = %s
            AND category = %s
            AND month = %s
            AND year = %s
            AND id != %s;
            """,
            (
                current_user_id,
                budget.category,
                budget.month,
                budget.year,
                budget_id
            )
        )

        duplicate_budget = cursor.fetchone()

        if duplicate_budget is not None:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Budget already exists for "
                    "this category and month"
                )
            )

        # Update budget
        cursor.execute(
            """
            UPDATE budgets
            SET
                category = %s,
                amount = %s,
                month = %s,
                year = %s
            WHERE id = %s
            AND user_id = %s
            RETURNING
                id,
                user_id,
                category,
                amount,
                month,
                year,
                created_at;
            """,
            (
                budget.category,
                budget.amount,
                budget.month,
                budget.year,
                budget_id,
                current_user_id
            )
        )

        updated_budget = cursor.fetchone()

        if updated_budget is None:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Budget not found"
            )

        connection.commit()

        return {
            "id": updated_budget[0],
            "user_id": updated_budget[1],
            "category": updated_budget[2],
            "amount": updated_budget[3],
            "month": updated_budget[4],
            "year": updated_budget[5],
            "created_at": updated_budget[6]
        }

    except HTTPException:

        connection.rollback()
        raise

    except Exception:

        connection.rollback()
        raise

    finally:

        cursor.close()
# ============================================================
# DELETE BUDGET
# ============================================================

@app.delete(
    "/budgets/{budget_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_budget(
    budget_id: int,
    current_user_id: int = Depends(get_current_user),
    connection=Depends(get_db)
):
    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM budgets
            WHERE id = %s
            AND user_id = %s;
            """,
            (
                budget_id,
                current_user_id
            )
        )

        if cursor.rowcount == 0:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Budget not found"
            )

        connection.commit()

    except HTTPException:

        connection.rollback()
        raise

    except Exception:

        connection.rollback()
        raise

    finally:

        cursor.close()


# ============================================================
# BUDGET VS ACTUAL SPENDING
# ============================================================

@app.get(
    "/budgets/comparison",
    response_model=list[BudgetComparison]
)
def get_budget_comparison(
    current_user_id: int = Depends(get_current_user),
    connection=Depends(get_db)
):
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            b.id,
            b.user_id,
            b.category,
            b.amount AS budget_amount,
            COALESCE(SUM(e.amount), 0) AS actual_spending,
            b.month,
            b.year
        FROM budgets b
        LEFT JOIN expenses e
            ON e.user_id = b.user_id
            AND e.category = b.category
            AND EXTRACT(MONTH FROM e.expense_date) = b.month
            AND EXTRACT(YEAR FROM e.expense_date) = b.year
        WHERE b.user_id = %s
        GROUP BY
            b.id,
            b.user_id,
            b.category,
            b.amount,
            b.month,
            b.year
        ORDER BY
            b.year DESC,
            b.month DESC;
        """,
        (current_user_id,)
    )

    results = cursor.fetchall()
    cursor.close()

    return build_budget_comparisons(results)

# ============================================================
# FINANCIAL INSIGHTS
# ============================================================

@app.get(
    "/insights",
    response_model=list[FinancialInsight]
)
def get_financial_insights(
    current_user_id: int = Depends(get_current_user),
    connection=Depends(get_db)
):
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            b.id,
            b.user_id,
            b.category,
            b.amount AS budget_amount,
            COALESCE(SUM(e.amount), 0) AS actual_spending,
            b.month,
            b.year
        FROM budgets b
        LEFT JOIN expenses e
            ON e.user_id = b.user_id
            AND e.category = b.category
            AND EXTRACT(MONTH FROM e.expense_date) = b.month
            AND EXTRACT(YEAR FROM e.expense_date) = b.year
        WHERE b.user_id = %s
        GROUP BY
            b.id,
            b.user_id,
            b.category,
            b.amount,
            b.month,
            b.year
        ORDER BY
            b.year DESC,
            b.month DESC;
        """,
        (current_user_id,)
    )

    results = cursor.fetchall()
    cursor.close()

    budget_comparisons = build_budget_comparisons(results)

    return generate_financial_insights(
        budget_comparisons
    )