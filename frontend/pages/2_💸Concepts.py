import streamlit as st
from streamlit import column_config as cc
from api.client import get, post, delete, put

st.set_page_config(page_title="Concepts", page_icon="💸", layout="wide")
st.title("Concepts")

# Data fetch
list_concepts_response = get("/concept")
concepts = list_concepts_response.json() if list_concepts_response.ok else []

# Lookups / Select options
concept_by_id_lookup = {t["id"]: t for t in concepts} if concepts else {}

with st.expander("➕ Create / ✏️ Update / ❌ Delete Concepts", expanded=False):
    col1, col2, col3 = st.columns([1.2, 1.2, 0.8])

    # Create
    with col1:
        with st.form("create_form", clear_on_submit=True):
            st.subheader("Create Concept")

            name = st.text_input("Name")
            is_ordinary = st.checkbox("Is Ordinary")
            periodicity = st.number_input(
                "Periodicity (in months)", min_value=0, max_value=12, step=1
            )
            description = st.text_area("Description")

            submitted = st.form_submit_button("Create")

            if submitted:
                rules = [
                    (name is None, "Name is required."),
                ]

                errors = [msg for condition, msg in rules if condition]

                if errors:
                    for e in errors:
                        st.error(e)
                else:
                    try:
                        resp = post(
                            "/concept",
                            {
                                "name": name,
                                "is_ordinary": is_ordinary,
                                "periodicity": periodicity if periodicity > 0 else None,
                                "description": description,
                            },
                        )

                        if resp.ok:
                            st.success("Concept created!")
                            st.rerun()
                        else:
                            st.error("Error creating Concept")
                    except Exception as e:
                        st.exception(e)

    # Update
    with col2:
        st.subheader("Update Concept")

        ids = list(concept_by_id_lookup.keys())
        selected_id = st.selectbox("Select Concept ID to Update", ids)

        if selected_id:
            tx = concept_by_id_lookup[selected_id]

            periodicity_raw = tx["periodicity"]
            periodicity_value = (
                int(periodicity_raw) if periodicity_raw is not None else 0
            )

            with st.form("update_form"):
                name_upd = st.text_input("Name", value=tx["name"])
                is_ordinary_upd = st.number_input(
                    "Is Ordinary", value=tx["is_ordinary"]
                )
                periodicity_upd = st.number_input(
                    "Periodicity", value=periodicity_value
                )
                description_upd = st.text_area("Description", value=tx["description"])

                update_submit = st.form_submit_button("Update")

                if update_submit:
                    resp = put(
                        f"/concept/{selected_id}",
                        {
                            "name": name_upd,
                            "is_ordinary": is_ordinary_upd,
                            "periodicity": periodicity_upd
                            if periodicity_upd > 0
                            else None,
                            "description": description_upd,
                        },
                    )

                    if resp.ok:
                        st.success("Concept updated!")
                        st.rerun()
                    else:
                        st.error("Update Concept failed")

    # Delete
    with col3:
        st.subheader("Delete Concept")

        id_to_delete = st.selectbox("Pick ID to delete", ids, key="delete_id")

        if st.button("Delete"):
            resp = delete(f"/concept/{id_to_delete}")
            if resp.ok:
                st.success("Concept deleted!")
                st.rerun()
            else:
                st.error("Delete Concept failed")

# Table
st.subheader("📄 All Concepts")

if concepts:
    st.dataframe(
        concepts,
        use_container_width=True,
        column_config={
            "id": cc.NumberColumn("ID", format="%d"),
            "name": cc.TextColumn("Name"),
            "is_ordinary": cc.CheckboxColumn("Is Ordinary"),
            "periodicity": cc.NumberColumn("Periodicity"),
            "description": cc.TextColumn("Description"),
        },
        column_order=["id", "name", "is_ordinary", "periodicity", "description"],
    )
else:
    st.error("Could not load Concepts")
