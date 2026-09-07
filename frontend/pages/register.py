import streamlit as st

from api import (
    register_user,
    handle_api_error
)


st.title("Create your SmartSpend account")


# ============================================================
# Registration Form
# ============================================================

name = st.text_input("Name")

email = st.text_input("Email")

password = st.text_input(
    "Password",
    type="password"
)


# ============================================================
# Registration
# ============================================================

if st.button("Create Account"):

    if not name or not email or not password:

        st.warning(
            "Please fill in all fields."
        )

        st.stop()


    response = register_user(
        name,
        email,
        password
    )


    if response is not None and response.status_code == 201:

        st.success(
            "Registration successful!"
        )


    elif response is not None and response.status_code == 400:

        st.error(
            "Email already registered."
        )


    elif response is not None and response.status_code == 422:

        st.error(
            "Please enter valid registration details."
        )


    else:

        handle_api_error(
            response,
            "registration"
        )