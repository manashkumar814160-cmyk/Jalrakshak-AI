import streamlit as st
from core.config import OFFLINE
from core.ui import page_header,disclaimer,apply_css
st.set_page_config(page_title="JalRakshak AI",page_icon="🌱",layout="wide",initial_sidebar_state="expanded")
apply_css()
st.sidebar.title("🌱 JalRakshak AI"); st.sidebar.caption("Predict the Need. Save Every Drop.")
if OFFLINE: st.sidebar.warning("OFFLINE DEMO DATA mode")
page_header("JalRakshak AI","Predict the Need. Save Every Drop.")
st.markdown("## Irrigation advice grounded in weather and crop information")
st.write("Understand whether a field may need irrigation today, see the reasons, and explore how a different weather scenario could change the estimate.")
st.info("Software-only advisory prototype. It estimates root-zone water; it does not use physical sensors or measure field moisture.")
from core.db import init_db,list_farms
init_db(); farms=list_farms(); c1,c2,c3=st.columns(3)
c1.metric("Farm profiles",len(farms)); c2.metric("Weather mode","Offline demo" if OFFLINE else "Live with fallback"); c3.metric("Physical sensors","None")
st.subheader("Start here"); st.write("Create a farm profile, then open Dashboard to see its estimate.")
st.page_link("pages/1_Farm_Setup.py",label="＋ Set up a farm",icon="🌾")
st.markdown("### How the estimate works"); st.write("Weather, crop stage, soil water capacity and irrigation history feed a simplified crop-water balance. The recommendation is a rule-based estimate, not a measurement or guarantee.")
disclaimer()
