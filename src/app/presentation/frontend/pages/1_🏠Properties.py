import streamlit as st
from streamlit import column_config as cc
from api.client import get, post, delete, put

st.set_page_config(page_title="Properties", page_icon="🏠", layout="wide")
st.title("Properties")

# Data fetch
list_properties_response = get("/property")
properties = list_properties_response.json() if list_properties_response.ok else []

# Lookups / Select options
property_by_id_lookup = {t["id"]: t for t in properties} if properties else {}

with st.expander("➕ Create / ✏️ Update / ❌ Delete Properties", expanded=False):
    col1, col2, col3 = st.columns([1.2, 1.2, 0.8])

    # Create
    with col1:
        with st.form("create_form", clear_on_submit=True):
            st.subheader("Create Property")

            location = st.text_input("Location")
            area = st.number_input("Area")
            valuation = st.number_input("Valuation", step=1.0, format="%.2f")
            details = st.text_area("Details")

            submitted = st.form_submit_button("Create")

            if submitted:
                rules = [
                    (location is None, "Location is required."),
                    (valuation == 0, "Valuation must be greater than 0."),
                ]

                errors = [msg for condition, msg in rules if condition]

                if errors:
                    for e in errors:
                        st.error(e)
                else:
                    try:
                        resp = post(
                            "/property",
                            {
                                "location": location,
                                "area": area if area > 0 else None,
                                "valuation": valuation,
                                "details": details,
                            },
                        )

                        if resp.ok:
                            st.success("Property created!")
                            st.rerun()
                        else:
                            st.error("Error creating Property")
                    except Exception as e:
                        st.exception(e)

    # Update
    with col2:
        st.subheader("Update Property")

        ids = list(property_by_id_lookup.keys())
        selected_id = st.selectbox("Select Property ID to Update", ids)

        if selected_id:
            tx = property_by_id_lookup[selected_id]

            valuation_raw = tx["valuation"]
            valuation_value = float(valuation_raw) if valuation_raw is not None else 0.0

            with st.form("update_form"):
                location_upd = st.text_input("Location", value=tx["location"])
                area_upd = st.number_input("Area", value=tx["area"])
                valuation_upd = st.number_input(
                    "Valuation", value=valuation_value, step=1.0, format="%.2f"
                )
                details_upd = st.text_area("Details", value=tx["details"])

                update_submit = st.form_submit_button("Update")

                if update_submit:
                    resp = put(
                        f"/property/{selected_id}",
                        {
                            "location": location_upd,
                            "area": area_upd if area_upd > 0 else None,
                            "valuation": valuation_upd,
                            "details": details_upd,
                        },
                    )

                    if resp.ok:
                        st.success("Property updated!")
                        st.rerun()
                    else:
                        st.error("Update Property failed")

    # Delete
    with col3:
        st.subheader("Delete Property")

        id_to_delete = st.selectbox("Pick ID to delete", ids, key="delete_id")

        if st.button("Delete"):
            resp = delete(f"/property/{id_to_delete}")
            if resp.ok:
                st.success("Property deleted!")
                st.rerun()
            else:
                st.error("Delete Property failed")

# Table
st.subheader("📄 All Properties")

if properties:
    st.dataframe(
        properties,
        use_container_width=True,
        column_config={
            "id": cc.NumberColumn("ID", format="%d"),
            "location": cc.TextColumn("Location"),
            "area": cc.NumberColumn("Area"),
            "valuation": cc.NumberColumn("Valuation", format="$ %.2f"),
            "details": cc.TextColumn("Details"),
        },
        column_order=["id", "location", "area", "valuation", "details"],
    )
else:
    st.error("Could not load Properties")
