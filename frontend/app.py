
import streamlit as st


st.set_page_config(
    page_title="SmartSpend",
    page_icon="💰",
    layout="wide"
)


# ============================================================
# SESSION INITIALIZATION
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "access_token" not in st.session_state:
    st.session_state["access_token"] = None


# ============================================================
# HOME PAGE
# ============================================================

st.title("💰 SmartSpend")

st.write(
    "Welcome to your personal finance management system."
)

st.info(
    "Use the pages in the sidebar to manage your "
    "expenses, budgets, and financial analytics."
)
