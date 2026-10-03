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

---

## 📡 API Documentation

SmartSpend exposes a REST API through FastAPI.

The API supports user authentication, expense management, financial
analytics, budget management, and financial insights.

### 🔐 Authentication

#### Register User

````text
POST /users/register


```text
POST /users/register

Creates a new SmartSpend user account.

Request body:

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword"
}

The password is securely hashed before being stored in the database.

Login User
POST /users/login

Authenticates an existing user and returns a JWT access token.

The login request uses form-based authentication:

username=<email>
password=<password>

Successful response:

{
  "access_token": "<JWT>",
  "token_type": "bearer"
}
💸 Expense Management

All expense endpoints require authentication.

Create Expense
POST /expenses

Creates an expense for the currently authenticated user.

Example request:

{
  "amount": 500.00,
  "category": "Food",
  "description": "Lunch",
  "expense_date": "2026-09-08"
}

The user ID is obtained from the authenticated JWT rather than being
provided by the client.

Get Expenses
GET /expenses

Returns expenses belonging to the authenticated user.

Supports filtering, sorting, and pagination.

Available query parameters include:

category
min_amount
max_amount
start_date
end_date
sort_by
sort_order
limit
offset
Get Expense
GET /expenses/{expense_id}

Returns a specific expense belonging to the authenticated user.

Update Expense
PUT /expenses/{expense_id}

Updates an existing expense belonging to the authenticated user.

Delete Expense
DELETE /expenses/{expense_id}

Deletes an expense belonging to the authenticated user.

📊 Analytics

All analytics endpoints require authentication.

Spending Summary
GET /analytics/summary

Returns:

Total spending
Expense count
Average expense
Highest expense
Lowest expense
Category Analytics
GET /analytics/categories

Returns spending grouped by category, including:

Category
Total spending
Expense count
Monthly Analytics
GET /analytics/monthly

Returns monthly spending totals.

Spending Trends
GET /analytics/trends

Returns monthly spending trends, including:

Year
Month
Total spending
Change from previous month
Percentage change
💰 Budget Management

All budget endpoints require authentication.

Create Budget
POST /budgets

Creates a category-based monthly budget.

Example:

{
  "category": "Food",
  "amount": 5000.00,
  "month": 9,
  "year": 2026
}
Get Budgets
GET /budgets

Returns budgets belonging to the authenticated user.

Update Budget
PUT /budgets/{budget_id}

Updates an existing budget belonging to the authenticated user.

Delete Budget
DELETE /budgets/{budget_id}

Deletes an existing budget belonging to the authenticated user.

Budget Comparison
GET /budgets/comparison

Compares budgeted amounts with actual spending.

The response includes information such as:

Budget amount
Actual spending
Budget utilization
Remaining budget
Budget status
Month
Year

Budget status can indicate whether spending is:

Healthy
Watch
Near Limit
Over Budget
💡 Financial Insights
Get Financial Insights
GET /insights

Generates financial insights based on budget utilization.

Possible insight types include:

budget_warning
budget_near_limit
over_budget

Insights can have different severity levels, including warnings and
critical over-budget notifications.

🔑 API Authentication

Protected endpoints require a JWT access token.

The token is sent using the HTTP Authorization header:

Authorization: Bearer <JWT>

Example:

GET /expenses
Authorization: Bearer eyJ...

FastAPI validates the token before allowing access to protected
resources.

The authenticated user's ID is extracted from the JWT and used to
enforce ownership of expenses and budgets.

🛡️ Authorization

Authentication determines who the user is.

Authorization determines which resources the user can access.

SmartSpend applies ownership checks to user-specific resources.

For example:

User A
  ↓
GET /expenses/15
  ↓
Is expense 15 owned by User A?
  ↓
Yes → Return expense
No  → Reject request

This prevents one authenticated user from accessing another user's
financial data.

📚 Interactive API Documentation

FastAPI automatically provides interactive API documentation.

When running SmartSpend locally:

http://127.0.0.1:8000/docs

The Swagger UI can be used to:

Explore available endpoints
View request schemas
View response schemas
Authorize with a JWT
Send test requests
Inspect API responses

A second documentation format is also available through FastAPI's
OpenAPI documentation.

📋 API Endpoint Summary
Method	Endpoint	Authentication
POST	/users/register	Public
POST	/users/login	Public
POST	/expenses	JWT
GET	/expenses	JWT
GET	/expenses/{expense_id}	JWT
PUT	/expenses/{expense_id}	JWT
DELETE	/expenses/{expense_id}	JWT
GET	/analytics/summary	JWT
GET	/analytics/categories	JWT
GET	/analytics/monthly	JWT
GET	/analytics/trends	JWT
POST	/budgets	JWT
GET	/budgets	JWT
PUT	/budgets/{budget_id}	JWT
DELETE	/budgets/{budget_id}	JWT
GET	/budgets/comparison	JWT
GET	/insights	JWT

### ⚠️ Important

Notice that I did **not** add endpoints that aren't part of your actual API. The documentation follows your current endpoint structure.

Also, the distinction between:

```text
Authentication → Who are you?
Authorization  → What are you allowed to access?

is particularly important for your interview explanation.

Step 2: Save

After replacing that section:

Ctrl + S

Then run:

git diff --check

If there is no output, the Markdown change has no whitespace problems.

Then run:

git status

You should see only:

modified: README.md
🛑 Don't commit yet

Send me the git status result after saving. I'll check that only the README changed, then we'll commit and push the API documentation to GitHub.

After that, 7.12 will be complete, and we'll return to 7.13 Deployment Platform Setup, where we can finally start evaluating the current backend hosting options. 🚀

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


text
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




this is current readme
Compare with other AI
Liner
Gemini
Claude

Yes 👍 I can see the current README exactly. Your first sections are already in place and look good:

# SmartSpend
├── Overview
├── Features
├── Tech Stack
└── Architecture

The architecture diagram is also properly inside the text code block. ✅

One important thing

Your README currently ends after the Architecture diagram.

So for 7.12 API Documentation, we should not replace the whole README. We simply need to continue after this line:

                              Data Storage

and the closing:

````

## Add this immediately after it

## 📡 API Documentation

SmartSpend exposes a REST API through FastAPI.

The API supports user authentication, expense management, financial
analytics, budget management, and financial insights.

### 🔐 Authentication

#### Register User

````text
POST /users/register

Creates a new SmartSpend user account.

Request body:

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword"
}

The password is securely hashed before being stored in the database.

Login User
POST /users/login

Authenticates an existing user and returns a JWT access token.

The login request uses form-based authentication:

username=<email>
password=<password>

Successful response:

{
  "access_token": "<JWT>",
  "token_type": "bearer"
}
💸 Expense Management

All expense endpoints require authentication.

Create Expense
POST /expenses

Creates an expense for the currently authenticated user.

Example request:

{
  "amount": 500.00,
  "category": "Food",
  "description": "Lunch",
  "expense_date": "2026-09-08"
}

The user ID is obtained from the authenticated JWT rather than being
provided by the client.

Get Expenses
GET /expenses

Returns expenses belonging to the authenticated user.

Supports filtering, sorting, and pagination.

Available query parameters include:

category
min_amount
max_amount
start_date
end_date
sort_by
sort_order
limit
offset
Get Expense
GET /expenses/{expense_id}

Returns a specific expense belonging to the authenticated user.

Update Expense
PUT /expenses/{expense_id}

Updates an existing expense belonging to the authenticated user.

Delete Expense
DELETE /expenses/{expense_id}

Deletes an expense belonging to the authenticated user.

📊 Analytics

All analytics endpoints require authentication.

Spending Summary
GET /analytics/summary

Returns:

Total spending
Expense count
Average expense
Highest expense
Lowest expense
Category Analytics
GET /analytics/categories

Returns spending grouped by category, including:

Category
Total spending
Expense count
Monthly Analytics
GET /analytics/monthly

Returns monthly spending totals.

Spending Trends
GET /analytics/trends

Returns monthly spending trends, including:

Year
Month
Total spending
Change from previous month
Percentage change
💰 Budget Management

All budget endpoints require authentication.

Create Budget
POST /budgets

Creates a category-based monthly budget.

Example:

{
  "category": "Food",
  "amount": 5000.00,
  "month": 9,
  "year": 2026
}
Get Budgets
GET /budgets

Returns budgets belonging to the authenticated user.

Update Budget
PUT /budgets/{budget_id}

Updates an existing budget belonging to the authenticated user.

Delete Budget
DELETE /budgets/{budget_id}

Deletes an existing budget belonging to the authenticated user.

Budget Comparison
GET /budgets/comparison

Compares budgeted amounts with actual spending.

The response includes:

Budget amount
Actual spending
Budget utilization
Remaining budget
Budget status
Month
Year

Budget status can indicate:

Healthy
Watch
Near Limit
Over Budget
💡 Financial Insights
Get Financial Insights
GET /insights

Generates financial insights based on budget utilization.

Possible insight types include:

budget_warning
budget_near_limit
over_budget

Insights can have different severity levels, including warnings and
critical over-budget notifications.

🔑 API Authentication

Protected endpoints require a JWT access token.

The token is sent using the HTTP Authorization header:

Authorization: Bearer <JWT>

Example:

GET /expenses
Authorization: Bearer eyJ...

FastAPI validates the token before allowing access to protected
resources.

The authenticated user's ID is extracted from the JWT and used to
enforce ownership of expenses and budgets.

🛡️ Authorization

Authentication determines who the user is.

Authorization determines which resources the user can access.

SmartSpend applies ownership checks to user-specific resources.

For example:

User A
  ↓
GET /expenses/15
  ↓
Is expense 15 owned by User A?
  ↓
Yes → Return expense
No  → Reject request

This prevents one authenticated user from accessing another user's
financial data.

📚 Interactive API Documentation

FastAPI provides interactive API documentation.

When running SmartSpend locally:

http://127.0.0.1:8000/docs

Swagger UI can be used to:

Explore available endpoints
View request schemas
View response schemas
Authorize with a JWT
Send test requests
Inspect API responses
📋 API Endpoint Summary
Method	Endpoint	Authentication
POST	/users/register	Public
POST	/users/login	Public
POST	/expenses	JWT
GET	/expenses	JWT
GET	/expenses/{expense_id}	JWT
PUT	/expenses/{expense_id}	JWT
DELETE	/expenses/{expense_id}	JWT
GET	/analytics/summary	JWT
GET	/analytics/categories	JWT
GET	/analytics/monthly	JWT
GET	/analytics/trends	JWT
POST	/budgets	JWT
GET	/budgets	JWT
PUT	/budgets/{budget_id}	JWT
DELETE	/budgets/{budget_id}	JWT
GET	/budgets/comparison	JWT
GET	/insights	JWT

### Then continue with your existing sections

After the API section, we should have:

```text
## 🗄️ Database Design
## 🧪 Testing
## 📁 Project Structure
## ⚙️ Installation
## 🔑 Environment Variables
## ▶️ Running the Application
## 🌐 Deployment
## 📸 Screenshots
## 🔮 Future Improvements
## 🎯 Project Goals
## 👤 Author
## 📄 License
````
