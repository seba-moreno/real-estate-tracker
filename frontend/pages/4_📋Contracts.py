from datetime import date, datetime
import streamlit as st
from streamlit import column_config as cc
from api.client import get, post, delete, put

st.set_page_config(page_title="Contracts", page_icon="📋", layout="wide")
st.title("Contracts")


# Utility functions
def validate_contract_dates(start_date: date, end_date: date):
    return end_date >= start_date


# Data fetch
list_contracts_response = get("/contract")
contracts = list_contracts_response.json() if list_contracts_response.ok else []

list_properties_response = get("/property")
properties = list_properties_response.json() if list_properties_response.ok else []

# Lookups / Select options
contract_by_id_lookup = {c["id"]: c for c in contracts} if contracts else {}
property_lookup = (
    {prop["location"]: prop["id"] for prop in properties} if properties else {}
)
property_ids_with_contracts = {c["property_id"] for c in contracts}

with st.expander("➕ Create / ✏️ Update / ❌ Delete Contracts", expanded=False):
    col1, col2, col3 = st.columns([1.2, 1.2, 0.8])

    # Create
    with col1:
        with st.form("create_form", clear_on_submit=True):
            st.subheader("Create Contract")

            property_selected = st.selectbox(
                "Property", property_lookup.keys(), index=None
            )
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
            details = st.text_area("Details")

            submitted = st.form_submit_button("Create")

            if submitted:
                selected_property_id = (
                    property_lookup[property_selected] if property_selected else None
                )

                rules = [
                    (property_selected is None, "Location is required."),
                    (
                        not validate_contract_dates(start_date, end_date),
                        "End Date must be after Start Date.",
                    ),
                    (
                        selected_property_id in property_ids_with_contracts,
                        "Properties can only have one contract.",
                    ),
                ]

                errors = [msg for condition, msg in rules if condition]

                if errors:
                    for e in errors:
                        st.error(e)
                else:
                    try:
                        resp = post(
                            "/contract",
                            {
                                "property_id": selected_property_id,
                                "start_date": start_date.isoformat(),
                                "end_date": end_date.isoformat(),
                                "details": details,
                            },
                        )

                        if resp.ok:
                            st.success("Contract created!")
                            st.rerun()
                        else:
                            st.error("Error creating Contract")
                    except Exception as e:
                        st.exception(e)

    # Update
    with col2:
        st.subheader("Update Contract")

        ids = list(contract_by_id_lookup.keys())
        selected_id = st.selectbox("Select Contract ID to Update", ids)

        if selected_id:
            tx = contract_by_id_lookup[selected_id]
            property_index = 0

            for key, value in property_lookup.items():
                if value == tx["property_id"]:
                    property_index = list(property_lookup.keys()).index(key)
                    break

            with st.form("update_form"):
                property_upd = st.selectbox(
                    "Property", property_lookup.keys(), index=property_index
                )
                start_date_upd = st.date_input(
                    "Start Date", value=datetime.fromisoformat(tx["start_date"])
                )
                end_date_upd = st.date_input(
                    "End Date", value=datetime.fromisoformat(tx["end_date"])
                )
                details_upd = st.text_area("Details", value=tx["details"])

                update_submit = st.form_submit_button("Update")

                if update_submit:
                    resp = put(
                        f"/contract/{selected_id}",
                        {
                            "property_id": property_lookup[property_upd],
                            "start_date": start_date_upd.isoformat(),
                            "end_date": end_date_upd.isoformat(),
                            "details": details_upd,
                        },
                    )

                    if resp.ok:
                        st.success("Contract updated!")
                        st.rerun()
                    else:
                        st.error("Update Contract failed")

    # Delete
    with col3:
        st.subheader("Delete Contract")

        id_to_delete = st.selectbox("Pick ID to delete", ids, key="delete_id")

        if st.button("Delete"):
            resp = delete(f"/contract/{id_to_delete}")
            if resp.ok:
                st.success("Contract deleted!")
                st.rerun()
            else:
                st.error("Delete Contract failed")

# Table
st.subheader("📄 All Contracts")

reversed_property_combo = {v: k for k, v in property_lookup.items()}

contracts_display = [
    {
        **{key: value for key, value in tx.items() if key not in ("property_id",)},
        "property": reversed_property_combo.get(tx.get("property_id"), "Unknown"),
    }
    for tx in (contracts or [])
]

if contracts_display:
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
    st.error("Could not load Contracts")
