import streamlit as st
import pandas as pd

def render_quick_actions(inventory_data: pd.DataFrame):
    st.subheader("⚡ Quick Actions")

    low_stock_items = inventory_data[inventory_data["In Stock"] < 5]

    if low_stock_items.empty:
        st.success("✅ All inventory levels are sufficient.")
    else:
        st.warning("⚠️ Low Stock Detected")
        st.dataframe(low_stock_items, hide_index=True)

        for _, row in low_stock_items.iterrows():
            item = row["Item"]
            if st.button(f"Restock {item}"):
                st.info(f"🔄 Restock initiated for {item} (simulated)")
