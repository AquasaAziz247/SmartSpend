
import streamlit as st

from api import (
    register_user,
    handle_api_error,
    get_response_json
)


st.title("Create your SmartSpend account")


# ============================================================
# REGISTRATION FORM
# ============================================================

name = st.text_input("Name")
email = st.text_input("Email")
password = st.text_input(
    "Password",
    type="password"
)


# ============================================================
# REGISTRATION
# ============================================================

if st.button("Create Account"):

    name = name.strip()
    email = email.strip()

    # Validate input
    if not name or not email or not password:
        st.warning("Please fill in all fields.")
        st.stop()

    # Call registration API
    response = register_user(
        name,
        email,
        password
    )

    if response is None:
        st.error(
            "Unable to connect to the server. "
            "Please try again."
        )
        st.stop()

    # Successful registration
    if response.status_code == 201:

        data = get_response_json(response)

        if not isinstance(data, dict):
            st.error(
                "Unexpected server response. "
                "Please try again."
            )
            st.stop()

        if not all(
            key in data
            for key in ("id", "name", "email")
        ):
            st.error(
                "Invalid registration response. "
                "Please try again."
            )
            st.stop()

        st.success(
            "Registration successful! "
            "You can now log in."
        )

    # Duplicate email
    elif response.status_code == 400:
        st.error("Email already registered.")

    # Invalid registration data
    elif response.status_code == 422:
        st.error(
            "Please enter valid registration details."
        )

    # Other API errors
    else:
        handle_api_error(
            response,
            "registration"
        )
