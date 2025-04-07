import streamlit as st
import pandas as pd
import os

DATA_PATH = os.path.join("data", "inventory.csv")

def render_inventory_editor():
    st.subheader("📦 Inventory Editor")

    try:
        df = pd.read_csv(DATA_PATH)
    except Exception as e:
        st.error(f"Failed to load inventory data: {str(e)}")
        return

    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="inventory_editor")

    if st.button("💾 Save Inventory", type="primary"):
        try:
            edited_df.to_csv(DATA_PATH, index=False)
            st.success("Inventory saved successfully ✅")
        except Exception as e:
            st.error(f"Failed to save inventory: {str(e)}")
