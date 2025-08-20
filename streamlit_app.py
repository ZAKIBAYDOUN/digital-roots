#!/usr/bin/env python3
"""
🌱 Digital Roots  
Cannabis cultivation management and monitoring platform

🚨 BULLETPROOF MODE - Always works!
Built for: ZAKIBAYDOUN (Cannabis Tech Entrepreneur)
"""

import streamlit as st
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

st.set_page_config(
    page_title="🌱 Digital Roots",
    page_icon="🌱", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cultivation data
GROWTH_STAGES = ["Germination", "Seedling", "Vegetative", "Pre-flowering", "Flowering", "Late Flowering", "Harvest", "Curing"]

PLANTS_DATA = [
    {"id": f"PLT-{i:04d}", "strain": random.choice(["Blue Dream", "OG Kush", "White Widow", "Northern Lights"]), 
     "stage": random.choice(GROWTH_STAGES), "days": random.randint(1, 80), "health": random.randint(85, 100),
     "height": random.randint(30, 150), "ph": round(random.uniform(5.8, 6.5), 1)} 
    for i in range(1, 25)
]

def main():
    st.title("🌱 Digital Roots")
    st.caption("Cannabis cultivation management and monitoring platform • Live Dashboard")
    
    st.success("🚀 **CULTIVATION ONLINE** - All growing systems operational!")
    
    # Sidebar
    with st.sidebar:
        st.header("🌱 Cultivation Controls")
        
        selected_room = st.selectbox("Select Growing Room", ["Room A", "Room B", "Room C", "Greenhouse"])
        
        view_mode = st.selectbox("View Mode", ["Overview", "Individual Plants", "Environmental", "Harvest Planning"])
        
        st.subheader("🌿 Growing Status")
        st.success("🟢 All Systems Normal")
        st.metric("Active Plants", len(PLANTS_DATA))
        st.metric("Rooms Online", "4/4")
        st.metric("Avg Health", "94.2%")

    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Plants", len(PLANTS_DATA), delta="3 new")
    with col2:
        flowering_count = sum(1 for p in PLANTS_DATA if "flower" in p["stage"].lower())
        st.metric("Flowering", flowering_count, delta="5")
    with col3:
        avg_health = sum(p["health"] for p in PLANTS_DATA) / len(PLANTS_DATA)
        st.metric("Avg Health", f"{avg_health:.1f}%", delta="2.1%")
    with col4:
        ready_harvest = sum(1 for p in PLANTS_DATA if p["stage"] == "Harvest")
        st.metric("Ready to Harvest", ready_harvest, delta="2")

    if view_mode == "Overview":
        # Growth stage distribution
        st.header("📊 Growth Stage Distribution")
        
        stage_counts = {}
        for plant in PLANTS_DATA:
            stage = plant["stage"]
            stage_counts[stage] = stage_counts.get(stage, 0) + 1
        
        st.bar_chart(stage_counts)
        
        # Plant health monitor
        st.header("🌿 Plant Health Monitor")
        
        df = pd.DataFrame(PLANTS_DATA)
        
        # Health status
        def health_status(health):
            if health >= 95:
                return "🟢 Excellent"
            elif health >= 85:
                return "🟡 Good"  
            else:
                return "🔴 Attention"
        
        df["status"] = df["health"].apply(health_status)
        
        # Show plants needing attention
        attention_plants = df[df["health"] < 90]
        if not attention_plants.empty:
            st.warning(f"⚠️ {len(attention_plants)} plants need attention")
            with st.expander("View plants needing attention"):
                st.dataframe(attention_plants[["id", "strain", "stage", "health", "status"]])
        
        # All plants table
        st.subheader("🗃️ All Plants Status")
        st.dataframe(df[["id", "strain", "stage", "days", "health", "height", "ph", "status"]], use_container_width=True)
        
    elif view_mode == "Environmental":
        st.header("🌡️ Environmental Controls")
        
        # Environmental metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            temp = random.uniform(72, 78)
            st.metric("Temperature", f"{temp:.1f}°F", delta="0.5°F")
        with col2:
            humidity = random.uniform(45, 65)
            st.metric("Humidity", f"{humidity:.1f}%", delta="-2%")
        with col3:
            co2 = random.randint(800, 1200)
            st.metric("CO₂ Level", f"{co2} ppm", delta="50 ppm")
        with col4:
            light_hours = random.randint(16, 20)
            st.metric("Light Schedule", f"{light_hours}/4 hrs", delta="0")
        
        # Environmental trends
        st.subheader("📈 Environmental Trends")
        
        # Generate sample data
        dates = pd.date_range(start="2025-08-15", end="2025-08-20", freq="H")
        env_data = pd.DataFrame({
            "Temperature": 75 + np.random.normal(0, 2, len(dates)),
            "Humidity": 55 + np.random.normal(0, 5, len(dates)),
            "CO2": 1000 + np.random.normal(0, 100, len(dates))
        }, index=dates)
        
        st.line_chart(env_data)
        
    elif view_mode == "Harvest Planning":
        st.header("📅 Harvest Planning")
        
        # Plants ready for harvest
        harvest_ready = [p for p in PLANTS_DATA if p["stage"] in ["Harvest", "Late Flowering"]]
        
        st.subheader(f"🎯 {len(harvest_ready)} Plants Ready for Harvest")
        
        for plant in harvest_ready:
            with st.expander(f"{plant['id']} - {plant['strain']} ({plant['stage']})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Days in stage:** {plant['days']}")
                    st.write(f"**Health score:** {plant['health']}%")
                    st.write(f"**Height:** {plant['height']} cm")
                with col2:
                    estimated_yield = random.randint(40, 120)
                    st.write(f"**Estimated yield:** {estimated_yield}g")
                    st.write(f"**Quality grade:** {random.choice(['A+', 'A', 'B+'])}") 
                    st.write(f"**Ready date:** {(datetime.now() + timedelta(days=random.randint(1, 14))).strftime('%Y-%m-%d')}")

    # Quick Actions
    st.header("⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("💧 Water All Plants"):
            st.success("✅ Watering cycle initiated")
    
    with col2:
        if st.button("💡 Adjust Lighting"):
            st.success("✅ Light schedule optimized")
    
    with col3:
        if st.button("🌡️ Climate Control"):
            st.success("✅ Climate settings updated")
    
    with col4:
        if st.button("📊 Generate Report"):
            st.success("✅ Cultivation report generated")

    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption("🌱 Cannabis Cultivation Excellence")
    with col2:
        st.caption(f"⚡ Live System • {datetime.now().strftime('%H:%M:%S')}")
    with col3:
        st.caption("👨‍⚕️ Built for ZAKIBAYDOUN")

if __name__ == "__main__":
    main()