from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class ExpenseCreate(BaseModel):
    user_id: int = Field(gt=0)
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