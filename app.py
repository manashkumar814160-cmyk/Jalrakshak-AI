import streamlit as st
from core.config import OFFLINE
from core.db import init_db
from core.ui import apply_css

st.set_page_config(
    page_title="JalRakshak AI",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed",
)
apply_css()
init_db()

st.sidebar.title("🌱 JalRakshak AI")
st.sidebar.caption("Predict the Need. Save Every Drop.")
st.sidebar.markdown("**Your path**\n\n1. Set up a farm\n2. Check today's advice\n3. Explore weather if useful")
if OFFLINE:
    st.sidebar.warning("Demo mode · sample weather")

navigation = st.navigation(
    {
        "GET STARTED": [
            st.Page("pages/0_Home.py", title="Home", icon="🏡", default=True),
            st.Page("pages/1_Farm_Setup.py", title="1 · Set up your farm", icon="🌾"),
            st.Page("pages/2_Dashboard.py", title="2 · Today's advice", icon="✅"),
        ],
        "EXPLORE": [
            st.Page("pages/3_Weather_Intelligence.py", title="Weather", icon="🌦"),
            st.Page("pages/4_Digital_Twin.py", title="Try a weather scenario", icon="🧪"),
            st.Page("pages/5_AI_Agronomist.py", title="Ask about this advice", icon="💬"),
            st.Page("pages/6_Water_Usage.py", title="Watering & field notes", icon="💧"),
        ],
    },
    position="sidebar",
)
navigation.run()
