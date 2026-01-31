from datetime import datetime
import streamlit as st
from streamlit import column_config as cc
from api.client import get, post, delete, put

st.set_page_config(page_title="Transactions", page_icon="💵", layout="wide")
st.title("Transactions")


# Utility functions
def validate_period(period_input: None | str):
    if not period_input:
        return False
    else:
        try:
            datetime.strptime(period_input, "%Y-%m")
            return True
        except ValueError:
            return False


# Data fetch
list_transactions_response = get("/transaction")
transactions = (
    list_transactions_response.json() if list_transactions_response.ok else []
)

list_properties_concepts_response = get("/properties-concepts/get-combos")
properties_concepts = (
    list_properties_concepts_response.json()
    if list_properties_concepts_response.ok
    else []
)

# Lookups / Select options
transaction_by_id_lookup = {t["id"]: t for t in transactions} if transactions else {}
properties_concepts_lookup = {
    f"{pc.get('property', {}).get('location', 'Unknown location')} - {(pc.get('concept') or {}).get('name', 'Unknown concept')}": pc.get(
        "id"
    )
    for pc in (properties_concepts or [])
}
transaction_type_lookup = {"Income": "income", "Expense": "expense"}


with st.expander("➕ Create / ✏️ Update / ❌ Delete Transactions", expanded=False):
    col1, col2, col3 = st.columns([1.2, 1.2, 0.8])

    # Create
    with col1:
        with st.form("create_form", clear_on_submit=True):
            st.subheader("Create Transaction")

            date = st.date_input("Date")
            properties_concepts_selected = st.selectbox(
                "Property Concept", properties_concepts_lookup.keys(), index=None
            )
            transaction_type = st.selectbox(
                "Transaction Type", transaction_type_lookup.keys(), index=None
            )
            period = st.text_input("Period (YYYY-MM format)")
            amount = st.number_input("Amount", step=1.0, format="%.2f")

            submitted = st.form_submit_button("Create")

            if submitted:
                rules = [
                    (not validate_period(period), "Period must follow YYYY-MM pattern"),
                    (
                        properties_concepts_selected is None,
                        "Property Concept is required.",
                    ),
                    (transaction_type is None, "Transaction Type is required."),
                    (not period, "Period is required."),
                    (amount == 0, "Amount must be greater than 0."),
                ]

                errors = [msg for condition, msg in rules if condition]

                if errors:
                    for e in errors:
                        st.error(e)
                else:
                    try:
                        assert properties_concepts_selected is not None
                        assert transaction_type is not None
                        resp = post(
                            "/transaction",
                            {
                                "date": date.isoformat(),
                                "properties_concepts_id": properties_concepts_lookup[
                                    properties_concepts_selected
                                ],
                                "transaction_type": transaction_type_lookup[
                                    transaction_type
                                ],
                                "period": period,
                                "amount": amount,
                            },
                        )
                        if resp.ok:
                            st.success("Transaction created!")
                            st.rerun()
                        else:
                            st.error("Error creating Transaction")
                    except Exception as e:
                        st.exception(e)

    # Update
    with col2:
        st.subheader("Update Transaction")

        ids = list(transaction_by_id_lookup.keys())
        selected_id = st.selectbox("Select Transaction ID to Update", ids)

        if selected_id:
            tx = transaction_by_id_lookup[selected_id]
            properties_concepts_index = 0
            transaction_type_index = 0

            for key, value in properties_concepts_lookup.items():
                if value == tx["properties_concepts_id"]:
                    properties_concepts_index = list(
                        properties_concepts_lookup.keys()
                    ).index(key)
                    break

            for key, value in transaction_type_lookup.items():
                if value == tx["transaction_type"]:
                    transaction_type_index = list(transaction_type_lookup.keys()).index(
                        key
                    )
                    break

            with st.form("update_form"):
                date_upd = st.date_input(
                    "Date", value=datetime.fromisoformat(tx["date"])
                )
                properties_concepts_upd = st.selectbox(
                    "Property Concept",
                    properties_concepts_lookup.keys(),
                    index=properties_concepts_index,
                )
                type_upd = st.selectbox(
                    "Transaction Type",
                    transaction_type_lookup.keys(),
                    index=transaction_type_index,
                )
                period_upd = st.text_input(
                    "Period (YYYY-MM format)", value=tx["period"]
                )
                amount_upd = st.number_input(
                    "Amount", value=float(tx["amount"]), step=1.0, format="%.2f"
                )

                update_submit = st.form_submit_button("Update")

                if update_submit:
                    if not validate_period(period_upd):
                        st.error("Period must follow YYYY-MM pattern")
                    else:
                        resp = put(
                            f"/transaction/{selected_id}",
                            {
                                "date": date_upd.isoformat(),
                                "properties_concepts_id": properties_concepts_lookup[
                                    properties_concepts_upd
                                ],
                                "transaction_type": transaction_type_lookup[type_upd],
                                "period": period_upd,
                                "amount": amount_upd,
                            },
                        )

                        if resp.ok:
                            st.success("Transaction updated!")
                            st.rerun()
                        else:
                            st.error("Update Transaction failed")

    # Delete
    with col3:
        st.subheader("Delete Transaction")

        id_to_delete = st.selectbox("Pick ID to delete", ids, key="delete_id")

        if st.button("Delete"):
            resp = delete(f"/transaction/{id_to_delete}")
            if resp.ok:
                st.success("Transaction deleted!")
                st.rerun()
            else:
                st.error("Delete Transaction failed")

# Table
st.subheader("📄 All Transactions")

reversed_properties_concepts_combo: dict[int, str] = {
    pc_id: label for label, pc_id in properties_concepts_lookup.items()
}
reversed_transaction_type_combo = {v: k for k, v in transaction_type_lookup.items()}

transactions_display = [
    {
        **{
            key: value
            for key, value in tx.items()
            if key not in ("properties_concepts_id", "transaction_type")
        },
        "property_concept": reversed_properties_concepts_combo.get(
            tx.get("properties_concepts_id"), "Unknown"
        ),
        "transaction_type": reversed_transaction_type_combo.get(
            tx.get("transaction_type"), "Unknown"
        ),
    }
    for tx in (transactions or [])
]

if transactions_display:
    st.dataframe(
        transactions_display,
        use_container_width=True,
        column_config={
            "id": cc.NumberColumn("ID", format="%d"),
            "date": cc.TextColumn("Date"),
            "property_concept": cc.TextColumn("Property Concept"),
            "transaction_type": cc.TextColumn("Transaction Type"),
            "period": cc.TextColumn("Period"),
            "amount": cc.NumberColumn("Amount", format="$ %.2f"),
        },
        column_order=[
            "id",
            "date",
            "property_concept",
            "transaction_type",
            "period",
            "amount",
        ],
    )
else:
    st.error("Could not load Transactions")
