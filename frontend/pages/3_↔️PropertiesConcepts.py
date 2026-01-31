import streamlit as st
from streamlit import column_config as cc
from api.client import get, post, delete, put

st.set_page_config(page_title="Properties Concepts", page_icon="↔️", layout="wide")
st.title("Properties Concepts")

# Utility functions

# Data fetch
list_properties_concepts_response = get("/properties-concepts/get-combos")
properties_concepts = (
    list_properties_concepts_response.json()
    if list_properties_concepts_response.ok
    else []
)

# Lookups / Select options
properties_concepts_by_id_lookup = (
    {t["id"]: t for t in properties_concepts} if properties_concepts else {}
)
properties_lookup = {
    p.get("property", {}).get("location", "Unknown property"): p.get("property_id")
    for p in (properties_concepts or [])
}
concepts_lookup = {
    c.get("concept", {}).get("name", "Unknown concept"): c.get("concept_id")
    for c in (properties_concepts or [])
}

with st.expander("➕ Create / ✏️ Update / ❌ Delete Transactions", expanded=False):
    col1, col2, col3 = st.columns([1.2, 1.2, 0.8])

    # Create
    with col1:
        with st.form("create_form", clear_on_submit=True):
            st.subheader("Create Property Concept")

            property_selected = st.selectbox(
                "Property", properties_lookup.keys(), index=None
            )
            concept_selected = st.selectbox(
                "Concept", concepts_lookup.keys(), index=None
            )
            enabled = st.checkbox("Enabled")

            submitted = st.form_submit_button("Create")

            if submitted:
                rules = [
                    (property_selected is None, "Property is required."),
                    (concept_selected is None, "Concept is required."),
                ]

                errors = [msg for condition, msg in rules if condition]

                if errors:
                    for e in errors:
                        st.error(e)
                else:
                    try:
                        assert property_selected is not None
                        assert concept_selected is not None
                        resp = post(
                            "/properties-concepts",
                            {
                                "property_id": properties_lookup[property_selected],
                                "concept_id": concepts_lookup[concept_selected],
                                "enabled": enabled,
                            },
                        )
                        if resp.ok:
                            st.success("Property Concept created!")
                            st.rerun()
                        else:
                            st.error("Error creating Property Concept")
                    except Exception as e:
                        st.exception(e)

    # Update
    with col2:
        st.subheader("Update Transaction")

        ids = list(properties_concepts_by_id_lookup.keys())
        selected_id = st.selectbox("Select Property Concept ID to Update", ids)

        if selected_id:
            tx = properties_concepts_by_id_lookup[selected_id]
            property_index = 0
            concept_index = 0

            for key, value in properties_lookup.items():
                if value == tx["property_id"]:
                    property_index = list(properties_lookup.keys()).index(key)
                    break

            for key, value in concepts_lookup.items():
                if value == tx["concept_id"]:
                    concept_index = list(concepts_lookup.keys()).index(key)
                    break

            with st.form("update_form"):
                property_upd = st.selectbox(
                    "Property", properties_lookup.keys(), index=property_index
                )
                concept_upd = st.selectbox(
                    "Concept", concepts_lookup.keys(), index=concept_index
                )
                enabled_upd = st.checkbox("Enabled", value=tx["enabled"])

                update_submit = st.form_submit_button("Update")

                if update_submit:
                    resp = put(
                        f"/properties-concepts/{selected_id}",
                        {
                            "property_id": properties_lookup[property_upd],
                            "concept_id": concepts_lookup[concept_upd],
                            "enabled": enabled_upd,
                        },
                    )

                    if resp.ok:
                        st.success("Property Concept updated!")
                        st.rerun()
                    else:
                        st.error("Update Property Concept failed")

    # Delete
    with col3:
        st.subheader("Delete Property Concept")

        id_to_delete = st.selectbox("Pick ID to delete", ids, key="delete_id")

        if st.button("Delete"):
            resp = delete(f"/properties-concepts/{id_to_delete}")
            if resp.ok:
                st.success("Property Concept deleted!")
                st.rerun()
            else:
                st.error("Delete Property Concept failed")

# Table
st.subheader("📄 All Properties Concepts")

properties_concepts_display = [
    {
        **{
            key: value
            for key, value in tx.items()
            if key not in ("property_id", "concept_id")
        },
        "property": tx.get("property").get("location"),
        "concept": tx.get("concept").get("name"),
    }
    for tx in (properties_concepts or [])
]

if properties_concepts_display:
    st.dataframe(
        properties_concepts_display,
        use_container_width=True,
        column_config={
            "id": cc.NumberColumn("ID", format="%d"),
            "property": cc.TextColumn("Property"),
            "concept": cc.TextColumn("Concept"),
            "enabled": cc.CheckboxColumn("Enabled"),
        },
        column_order=["id", "property", "concept", "enabled"],
    )
else:
    st.error("Could not load Properties Concepts")
