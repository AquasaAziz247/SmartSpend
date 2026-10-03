
import os
from urllib.parse import urlsplit

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


# ============================================================
# API BASE URL CONFIGURATION AND VALIDATION
# ============================================================

raw_base_url = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000",
).strip()

if not raw_base_url:
    raise ValueError(
        "API_BASE_URL is empty. "
        "Please configure a valid API URL."
    )

try:
    parsed_url = urlsplit(raw_base_url)

    # Accessing port also validates its format and range.
    _ = parsed_url.port

    if (
        parsed_url.scheme not in ("http", "https")
        or not parsed_url.hostname
        or any(char.isspace() for char in raw_base_url)
        or parsed_url.query
        or parsed_url.fragment
        or parsed_url.username is not None
        or parsed_url.password is not None
    ):
        raise ValueError

except ValueError:
    raise ValueError(
        "Invalid API_BASE_URL. "
        "Use a valid HTTP or HTTPS URL without "
        "credentials, query parameters or fragments."
    ) from None

BASE_URL = raw_base_url.rstrip("/")

REQUEST_TIMEOUT = 10


# ============================================================
# Authentication Headers
# ============================================================

def get_auth_headers():
    token = st.session_state.get("access_token")

    if not token:
        return None

    return {
        "Authorization": f"Bearer {token}",
    }


# ============================================================
# Centralized HTTP Request Handling
# ============================================================

def _send_request(method, endpoint, **kwargs):
    try:
        return requests.request(
            method,
            f"{BASE_URL}{endpoint}",
            timeout=REQUEST_TIMEOUT,
            **kwargs
        )

    except requests.exceptions.Timeout:
        return None

    except requests.exceptions.ConnectionError:
        return None

    except requests.exceptions.RequestException:
        return None


# ============================================================
# Authenticated Request
# ============================================================

def authenticated_request(method, endpoint, **kwargs):
    headers = get_auth_headers()

    if headers is None:
        return None

    # Merge custom headers with authentication headers.
    custom_headers = kwargs.pop("headers", {})
    headers.update(custom_headers)

    return _send_request(
        method,
        endpoint,
        headers=headers,
        **kwargs
    )


# ============================================================
# Authentication API
# ============================================================

def login_user(email, password):
    return _send_request(
        "POST",
        "/users/login",
        data={
            "username": email,
            "password": password,
        },
    )


def register_user(name, email, password):
    return _send_request(
        "POST",
        "/users/register",
        json={
            "name": name,
            "email": email,
            "password": password,
        },
    )


# ============================================================
# Expense API
# ============================================================

def create_expense(
    amount,
    category,
    description,
    expense_date,
):
    return authenticated_request(
        "POST",
        "/expenses",
        json={
            "amount": amount,
            "category": category,
            "description": description,
            "expense_date": expense_date,
        },
    )


def get_expenses():
    return authenticated_request(
        "GET",
        "/expenses",
    )


def update_expense(
    expense_id,
    amount,
    category,
    description,
    expense_date,
):
    return authenticated_request(
        "PUT",
        f"/expenses/{expense_id}",
        json={
            "amount": amount,
            "category": category,
            "description": description,
            "expense_date": expense_date,
        },
    )


def delete_expense(expense_id):
    return authenticated_request(
        "DELETE",
        f"/expenses/{expense_id}",
    )


# ============================================================
# Analytics API
# ============================================================

def get_summary():
    return authenticated_request(
        "GET",
        "/analytics/summary",
    )


def get_categories():
    return authenticated_request(
        "GET",
        "/analytics/categories",
    )


def get_monthly():
    return authenticated_request(
        "GET",
        "/analytics/monthly",
    )


def get_trends():
    return authenticated_request(
        "GET",
        "/analytics/trends",
    )


# ============================================================
# Budget API
# ============================================================

def get_budgets():
    return authenticated_request(
        "GET",
        "/budgets",
    )


def get_budget_comparison():
    return authenticated_request(
        "GET",
        "/budgets/comparison",
    )


def get_insights():
    return authenticated_request(
        "GET",
        "/insights",
    )


def create_budget(
    category,
    amount,
    month,
    year,
):
    return authenticated_request(
        "POST",
        "/budgets",
        json={
            "category": category,
            "amount": amount,
            "month": month,
            "year": year,
        },
    )


def update_budget(
    budget_id,
    category,
    amount,
    month,
    year,
):
    return authenticated_request(
        "PUT",
        f"/budgets/{budget_id}",
        json={
            "category": category,
            "amount": amount,
            "month": month,
            "year": year,
        },
    )


def delete_budget(budget_id):
    return authenticated_request(
        "DELETE",
        f"/budgets/{budget_id}",
    )


# ============================================================
# Safe JSON Response Handling
# ============================================================

def get_response_json(response):
    if response is None:
        return None

    try:
        return response.json()

    except ValueError:
        st.error(
            "SmartSpend received an invalid response "
            "from the server."
        )

        return None


# ============================================================
# API Error Handling
# ============================================================

def handle_api_error(response, action="request"):
    if response is None:
        st.error(
            "Unable to connect to SmartSpend API. "
            "Please check your connection and try again."
        )

        return True

    if response.status_code == 401:
        st.session_state["access_token"] = None
        st.session_state["logged_in"] = False

        st.error(
            "Your session has expired. "
            "Please login again."
        )

        return True

    if response.status_code == 404:
        st.error(
            f"The requested {action} was not found."
        )

        return True

    if response.status_code == 409:
        st.error(
            "This request conflicts with existing data."
        )

        return True

    if response.status_code == 422:
        st.error(
            "Invalid data. Please check your input."
        )

        return True

    if response.status_code >= 500:
        st.error(
            "SmartSpend server error. "
            "Please try again later."
        )

        return True

    if response.status_code >= 400:
        st.error(
            f"Unable to complete {action}."
        )

        return True

    return False


# ============================================================
# Session Management
# ============================================================

def logout_user():
    st.session_state["access_token"] = None
    st.session_state["logged_in"] = False
