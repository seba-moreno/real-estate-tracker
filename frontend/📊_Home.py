# import streamlit as st
# from streamlit import column_config as cc
# from api.client import get

# st.set_page_config(page_title="Real Estate Tracker",page_icon="📋", layout="wide")
# st.title("Real Estate Tracker")

# st.subheader("Check expiring Contracts")
# months_to_check = st.selectbox("Select months ahead to check expiring contracts", [1,2,3,4,5,6,7,8,9,10,11,12], key="delete_id")

# #Data fetch
# list_contracts_response = get(f"/contract/ending-in/{months_to_check}")
# contracts = list_contracts_response.json() if list_contracts_response.ok else []

# property_response = get("/property")
# properties = property_response.json() if property_response.ok else []

# transaction_balance_response = get("/transaction/balance")
# balance = transaction_balance_response.json() if transaction_balance_response.ok else {}

# #Lookup
# property_lookup = {prop["id"]: prop["location"] for prop in properties} if properties else {}

# #Table
# contracts_display = [
#     {
#         **{key: value
#            for key, value in tx.items()
#            if key not in ("property_id",)},
#         "property": property_lookup.get(tx.get("property_id"), "Unknown"),
#     }
#     for tx in (contracts or [])
# ]

# if contracts_display:
#     st.dataframe(
#         contracts_display,
#         use_container_width=True,
#         column_config={
#             "id": cc.NumberColumn("ID", format="%d"),
#             "property": cc.TextColumn("Property"),
#             "start_date": cc.TextColumn("Start Date"),
#             "end_date": cc.TextColumn("End Date"),
#             "details": cc.TextColumn("Details"),
#         },
#         column_order=["id", "property", "start_date", "end_date", "details"],
# )
# else:
#     st.warning(f"No Contracts ending within the next {months_to_check} month/s")


# st.subheader("Transactions balance")
# st.write(balance.get("balance"))


import streamlit as st
from streamlit import column_config as cc
from api.client import get

# -------------------------------------------------
# Page Config
# -------------------------------------------------
st.set_page_config(page_title="Real Estate Tracker", page_icon="📋", layout="wide")

# -------------------------------------------------
# Title Section
# -------------------------------------------------
st.markdown(
    """
    <h1 style="text-align:center; margin-bottom:0;">
        📋 Real Estate Tracker
    </h1>
    <p style="text-align:center; font-size:18px; color:#666;">
        Monitor contracts, financial performance, and assets at a glance.
    </p>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

# Balance section
balance_res = get("/transaction/balance")
balance = balance_res.json().get("balance") if balance_res.ok else 0

st.subheader("💰 Transactions Balance")
color = "green" if balance >= 0 else "red"
st.markdown(
    f"""
    <div style="padding:12px; border-radius:8px; background:#f7f7f7;">
        <p style="margin:0; color:#666;">Current Balance</p>
        <h2 style="margin:0; color:{color};">
            ${balance:,.2f}
        </h2>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

# Contracts Expiring section
st.subheader("🔎 Check Expiring Contracts")
months_to_check = st.selectbox(
    "Select months ahead:",
    list(range(1, 13)),
    key="delete_id",
    index=11,
)

contracts_res = get(f"/contract/ending-in/{months_to_check}")
contracts = contracts_res.json() if contracts_res.ok else []
properties_res = get("/property")
properties = properties_res.json() if properties_res.ok else []


property_lookup = {p["id"]: p["location"] for p in properties}
contracts_display = [
    {
        **{k: v for k, v in c.items() if k != "property_id"},
        "property": property_lookup.get(c.get("property_id"), "Unknown"),
    }
    for c in contracts
]

if contracts_display:
    st.subheader(f"📄 Contracts Ending in the Next {months_to_check} Month(s)")
    st.dataframe(
        contracts_display,
        use_container_width=True,
        column_config={
            "id": cc.NumberColumn("ID", format="%d"),
            "property": cc.TextColumn("Property"),
            "start_date": cc.TextColumn("Start Date"),
            "end_date": cc.TextColumn("End Date"),
            "details": cc.TextColumn("Details"),
        },
        column_order=["id", "property", "start_date", "end_date", "details"],
    )
else:
    st.info(f"✨ No contracts ending within the next **{months_to_check} month(s)**.")
