from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class ExpenseCreate(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    category: str = Field(min_length=1, max_length=50)
    description: str | None = None
    expense_date: date

class ExpenseResponse(BaseModel):
    id: int
    user_id: int
    amount: Decimal
    category: str
    description: str | None
    expense_date: date

class UserRegister(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8)

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class ExpenseSummary(BaseModel):
    total_spending: Decimal | None
    expense_count: int
    average_expense: Decimal | None
    highest_expense: Decimal | None
    lowest_expense: Decimal | None

class CategorySummary(BaseModel):
    category: str
    total_spending: Decimal
    expense_count: int

class MonthlySummary(BaseModel):
    year: int
    month: int
    total_spending: Decimal

class SpendingTrend(BaseModel):
    year: int
    month: int
    total_spending: Decimal
    change: Decimal | None
    percentage_change: Decimal | None

class BudgetCreate(BaseModel):
    category: str = Field(min_length=1, max_length=50)
    amount: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2
    )
    month: int = Field(ge=1, le=12)
    year: int


class BudgetUpdate(BaseModel):
    category: str = Field(min_length=1, max_length=50)
    amount: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2
    )
    month: int = Field(ge=1, le=12)
    year: int

class BudgetResponse(BaseModel):
    id: int
    user_id: int
    category: str
    amount: Decimal
    month: int
    year: int
    created_at: datetime

class FinancialInsight(BaseModel):
    type: str
    category: str | None
    message: str
    severity: str

class BudgetComparison(BaseModel):
    id: int
    user_id: int
    category: str
    budget_amount: Decimal
    actual_spending: Decimal
    utilization: Decimal | None
    remaining_budget: Decimal
    status: str
    month: int
    year: int