import streamlit as st
from datetime import date
from core.db import init_db,save_farm,list_farms,delete_farm
from core.crops import CROPS
from core.soils import SOILS,EFFICIENCY
from core.weather import search_places
from core.ui import apply_css
st.set_page_config(page_title="Farm Setup | JalRakshak",page_icon="🌾",layout="wide"); init_db(); st.title("🌾 Farm Setup")
apply_css()
with st.form("farm"):
    name=st.text_input("Farm name",value="Demo Farm"); place=st.text_input("Search location",value="Hyderabad"); results=search_places(place)
    selected=st.selectbox("Choose a location",results,format_func=lambda x:f"{x['name']}, {x.get('country','')}")
    crop=st.selectbox("Crop",list(CROPS)); soil=st.selectbox("Soil",list(SOILS)); st.caption(SOILS[soil][1])
    method=st.selectbox("Irrigation method",list(EFFICIENCY)); area=st.number_input("Area (acres)",min_value=.01,value=1.0,step=.1)
    sowing=st.date_input("Sowing date",value=date.today()); harvest=st.date_input("Harvest date (optional)",value=None)
    submitted=st.form_submit_button("Save farm",type="primary")
if submitted:
    try:
        fid=save_farm({"name":name.strip() or "Farm","place":selected["name"],"latitude":selected["latitude"],"longitude":selected["longitude"],"crop":crop,"soil":soil,"irrigation_method":method,"area_acres":area,"sowing_date":sowing.isoformat(),"harvest_date":harvest.isoformat() if harvest else None}); st.session_state["farm_id"]=fid; st.success("Farm saved.")
    except Exception as e: st.error(f"Could not save farm: {e}")
st.subheader("Saved farms"); farms=list_farms()
if not farms: st.info("No farms saved yet.")
for farm in farms:
    col1,col2=st.columns([4,1]); col1.write(f"**{farm['name']}** · {farm['place']} · {farm['crop']} · {farm['area_acres']} acres")
    if col2.button("Use farm",key=f"use{farm['id']}"): st.session_state["farm_id"]=farm["id"]; st.success("Selected for this session.")
    if st.button("Delete",key=f"delete{farm['id']}"): delete_farm(farm['id']); st.rerun()
