import streamlit as st

from api import (
    login_user,
    handle_api_error,
    get_response_json
)


st.title("Login")


# ============================================================
# Login Form
# ============================================================

with st.form("login_form"):

    email = st.text_input("Email")

    password = st.text_input(
        "Password",
        type="password"
    )

    submitted = st.form_submit_button("Login")


# ============================================================
# Login
# ============================================================

if submitted:

    if not email or not password:

        st.warning(
            "Please enter both email and password."
        )

        st.stop()


    response = login_user(
        email,
        password
    )


    if response is not None and response.status_code == 200:

        data = get_response_json(response)

        if data is None:
            st.stop()

        st.session_state["access_token"] = (
            data["access_token"]
        )

        st.session_state["logged_in"] = True

        st.success("Login successful!")


    elif response is not None and response.status_code == 401:

        st.error(
            "Invalid email or password."
        )


    elif response is not None and response.status_code == 422:

        st.error(
            "Please enter valid login details."
        )


    else:

        handle_api_error(
            response,
            "login"
        )