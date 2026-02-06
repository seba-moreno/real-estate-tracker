import streamlit as st

def render_sidebar():
    with st.sidebar:
        st.title("Real Estate Tracker")
        st.markdown("---")

        st.page_link("home.py", label="Home")
        st.page_link("pages/properties.py", label="🏡 Properties")
        st.page_link("pages/concepts.py", label="💸 Concepts")
        st.page_link("pages/properties_concepts.py", label="↔️ Properties Concepts")
        st.page_link("pages/contracts.py", label="📄 Contracts")
        st.page_link("pages/transactions.py", label="💰 Transactions")

        st.markdown("---")

        if st.button("Logout"):
            st.session_state.token = None
            st.rerun()