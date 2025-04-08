import streamlit as st

def render_analytics_summary():
    st.subheader("📍 Analytics Summary")
    
    st.markdown("### Delivery Zone Analysis")
    st.write("""
        This section shows high-level statistics and performance insights for your delivery zones.
    """)

    # Simulated zone stats
    zone_data = {
        "Zone A": {"Routes": 10, "Avg Time (hrs)": 1.2, "Avg Emissions (kg)": 3.1},
        "Zone B": {"Routes": 8, "Avg Time (hrs)": 1.5, "Avg Emissions (kg)": 3.8},
        "Zone C": {"Routes": 6, "Avg Time (hrs)": 2.0, "Avg Emissions (kg)": 5.2},
    }

    for zone, stats in zone_data.items():
        with st.expander(f"📦 {zone}"):
            st.write(f"- Total Routes: {stats['Routes']}")
            st.write(f"- Average Delivery Time: {stats['Avg Time (hrs)']} hours")
            st.write(f"- Average CO₂ Emissions: {stats['Avg Emissions (kg)']} kg")

    st.markdown("### Insights")
    st.success("✅ Zone A is performing best with lowest emissions and fastest delivery.")
    st.warning("⚠️ Zone C has higher emissions and slower deliveries — consider optimization.")
