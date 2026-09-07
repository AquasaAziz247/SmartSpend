import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000",
)

REQUEST_TIMEOUT = 10


# ============================================================
# Authentication Headers
# ============================================================

def get_auth_headers():
    if "access_token" not in st.session_state:
        return None

    token = st.session_state["access_token"]

    return {
        "Authorization": f"Bearer {token}",
    }


# ============================================================
# Authenticated Request
# ============================================================

def authenticated_request(
    method,
    endpoint,
    **kwargs
):

    headers = get_auth_headers()

    if headers is None:
        return None

    if "headers" in kwargs:
        headers.update(kwargs["headers"])

    try:

        return requests.request(
            method,
            f"{BASE_URL}{endpoint}",
            headers=headers,
            timeout=REQUEST_TIMEOUT,
            **{
                key: value
                for key, value in kwargs.items()
                if key != "headers"
            }
        )

    except requests.exceptions.Timeout:

        st.error(
            "SmartSpend API request timed out. "
            "Please try again."
        )

        return None

    except requests.exceptions.ConnectionError:

        st.error(
            "Unable to connect to SmartSpend API. "
            "Please make sure the backend server is running."
        )

        return None

    except requests.exceptions.RequestException:

        st.error(
            "An unexpected network error occurred."
        )

        return None


# ============================================================
# Authentication API
# ============================================================

def login_user(email, password):

    try:

        return requests.post(
            f"{BASE_URL}/users/login",
            data={
                "username": email,
                "password": password
            },
            timeout=REQUEST_TIMEOUT
        )

    except requests.exceptions.Timeout:

        st.error(
            "SmartSpend API request timed out. "
            "Please try again."
        )

        return None

    except requests.exceptions.ConnectionError:

        st.error(
            "Unable to connect to SmartSpend API. "
            "Please make sure the backend server is running."
        )

        return None

    except requests.exceptions.RequestException:

        st.error(
            "An unexpected network error occurred."
        )

        return None


def register_user(name, email, password):

    try:

        return requests.post(
            f"{BASE_URL}/users/register",
            json={
                "name": name,
                "email": email,
                "password": password
            },
            timeout=REQUEST_TIMEOUT
        )

    except requests.exceptions.Timeout:

        st.error(
            "SmartSpend API request timed out. "
            "Please try again."
        )

        return None

    except requests.exceptions.ConnectionError:

        st.error(
            "Unable to connect to SmartSpend API. "
            "Please make sure the backend server is running."
        )

        return None

    except requests.exceptions.RequestException:

        st.error(
            "An unexpected network error occurred."
        )

        return None


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
            "Please make sure the backend server is running."
        )

        return True

    if response.status_code == 401:
        st.session_state.pop(
            "access_token",
            None,
        )

        st.session_state.pop(
            "logged_in",
            None,
        )

        st.error(
            "Authentication failed. Please login again."
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
    st.session_state.pop(
        "access_token",
        None,
    )

    st.session_state.pop(
        "logged_in",
        None,
    )