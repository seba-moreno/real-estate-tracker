import streamlit as st
import requests

API_BASE = "http://localhost:8000/api/v1"

def ensure_auth():
    # Hide Streamlit's default multipage navigation
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"] {display: none;}
        </style>
    """, unsafe_allow_html=True)

    if "token" not in st.session_state:
        st.session_state.token = None

    if not st.session_state.token:
        # Hide full sidebar except the container
        st.markdown("""
            <style>
                section[data-testid="stSidebar"] {display: none;}
            </style>
        """, unsafe_allow_html=True)

        with st.expander("🔐 Login / Register", expanded=True):
            tab_login, tab_register = st.tabs(["Login", "Register"])

            with tab_login:
                c1, c2 = st.columns(2)
                username = c1.text_input("Username")
                password = c2.text_input("Password", type="password")

                if st.button("Sign In"):
                    resp = requests.post(
                        f"{API_BASE}/auth/login",
                        json={"username": username, "password": password},
                        timeout=10,
                    )
                    if resp.ok:
                        st.session_state.token = resp.json()["access_token"]
                        st.success("Logged in!")
                        st.rerun()
                    else:
                        st.error(resp.json().get("detail", "Login failed"))

            with tab_register:
                c1, c2 = st.columns(2)
                user = c1.text_input("New Username")
                pwd = c2.text_input("New Password", type="password")
                email = st.text_input("Email (optional)")

                if st.button("Create Account"):
                    resp = requests.post(
                        f"{API_BASE}/auth/register",
                        json={"username": user, "password": pwd, "email": email or None},
                    )
                    if resp.ok:
                        st.success("Account created! You can now log in.")
                    else:
                        st.error(resp.json().get("detail", "Registration failed"))

        st.stop()

    return st.session_state.token