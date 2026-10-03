
import streamlit as st

from api import (
    login_user,
    handle_api_error,
    get_response_json
)


st.title("Login")


# ============================================================
# LOGIN FORM
# ============================================================

with st.form("login_form"):

    email = st.text_input("Email")

    password = st.text_input(
        "Password",
        type="password"
    )

    submitted = st.form_submit_button("Login")


# ============================================================
# LOGIN
# ============================================================

if submitted:

    # Validate input
    email = email.strip()

    if not email or not password:
        st.warning(
            "Please enter both email and password."
        )
        st.stop()

    # Call login API
    response = login_user(email, password)

    if response is None:
        st.error(
            "Unable to connect to the server. "
            "Please try again."
        )
        st.stop()

    # Successful login
    if response.status_code == 200:

        data = get_response_json(response)

        # Validate response format
        if not isinstance(data, dict):
            st.error(
                "Unexpected server response. "
                "Please try again."
            )
            st.stop()

        access_token = data.get("access_token")
        token_type = data.get("token_type")

        if (
            not isinstance(access_token, str)
            or not access_token.strip()
            or token_type != "bearer"
        ):
            st.error(
                "Invalid login response. "
                "Please try again."
            )
            st.stop()

        # Store authentication state
        st.session_state["access_token"] = access_token
        st.session_state["logged_in"] = True

        st.success("Login successful!")

        st.rerun()

    # Invalid credentials
    elif response.status_code == 401:
        st.error(
            "Invalid email or password."
        )

    # Validation error
    elif response.status_code == 422:
        st.error(
            "Please enter valid login details."
        )

    # Other API errors
    else:
        handle_api_error(
            response,
            "login"
        )
