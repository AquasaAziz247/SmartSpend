# 💰 SmartSpend

SmartSpend is a personal finance management application that helps users
track expenses, manage category-based budgets, analyze spending patterns,
and receive financial insights.

The project is built using a separated frontend, backend, and database
architecture with authentication, authorization, automated testing, and
environment-based configuration.

---

## 🚀 Features

### 👤 User Authentication

- User registration
- User login
- Password hashing using bcrypt
- JWT-based authentication
- Protected API endpoints
- User-specific data access

### 💸 Expense Management

- Create expenses
- View expenses
- View individual expenses
- Update expenses
- Delete expenses
- Filter expenses by category
- Filter by amount range
- Filter by date range
- Sort expenses
- Pagination support

### 📊 Financial Analytics

SmartSpend provides:

- Total spending
- Expense count
- Average expense
- Highest expense
- Lowest expense
- Category-wise spending
- Monthly spending
- Monthly spending trends
- Percentage changes between months

### 💰 Budget Management

- Create category-based budgets
- View budgets
- Update budgets
- Delete budgets
- Prevent duplicate budgets for the same category and month
- Compare budget against actual spending
- Calculate budget utilization
- Calculate remaining budget
- Track budget status

### 💡 Financial Insights

SmartSpend generates budget-related financial insights based on spending
and budget utilization.

Examples include:

- Approaching budget limit
- Budget warning
- Over-budget alerts

---

## 🛠️ Tech Stack

| Layer             | Technology    |
| ----------------- | ------------- |
| Frontend          | Streamlit     |
| Backend           | FastAPI       |
| Database          | PostgreSQL    |
| Language          | Python        |
| Authentication    | JWT           |
| Password Hashing  | bcrypt        |
| API Communication | REST / HTTP   |
| Database Driver   | psycopg2      |
| Validation        | Pydantic      |
| Testing           | pytest        |
| API Testing       | HTTPX         |
| Configuration     | python-dotenv |
| Server            | Uvicorn       |

---

## 🏗️ Architecture

```text
                    SmartSpend
                         │
          ┌──────────────┼──────────────┐
          ↓              ↓              ↓
      Frontend         Backend       Database
     Streamlit         FastAPI      PostgreSQL
          │              │              │
          │     HTTP     │              │
          └─────────────→│              │
                         │              │
                  Business Logic        │
                         │              │
                         └─────────────→│
                                        │
                              Data Storage
```
