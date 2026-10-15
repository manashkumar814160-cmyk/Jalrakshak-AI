import streamlit as st
from datetime import date
from core.db import init_db,save_farm,list_farms,delete_farm
from core.crops import CROPS
from core.soils import SOILS,EFFICIENCY
from core.weather import search_places
from core.ui import page_header
init_db()
page_header("Step 1 · Set up your farm", "This takes about one minute. Your details are saved on this computer.")
st.caption("Start with where the field is, then add the crop and soil details. The estimates are only as good as these inputs.")

st.markdown("#### 1. Choose the field location")
with st.form("farm"):
    place=st.text_input("Town or village",value="Hyderabad",help="Choose the nearest listed place; the location is used to request weather.")
    results=search_places(place)
    selected=st.selectbox("Nearest match",results,format_func=lambda x:f"{x['name']}, {x.get('country','')}")
    st.markdown("#### 2. Add crop and field details")
    name=st.text_input("Give this field a name",value="My field",help="For example: North field or Demo farm.")
    crop=st.selectbox("What are you growing?",list(CROPS))
    soil=st.selectbox("What kind of soil is it?",list(SOILS),help="Choose the closest match. If you are unsure, ask a local agriculture worker.")
    st.caption(SOILS[soil][1])
    area=st.number_input("Field size (acres)",min_value=.01,value=1.0,step=.1)
    method=st.selectbox("How do you water the field?",list(EFFICIENCY))
    sowing=st.date_input("When was this crop planted?",value=date.today())
    harvest=st.date_input("Expected harvest date (optional)",value=None)
    submitted=st.form_submit_button("Save field and continue",type="primary",width="stretch")
if submitted:
    try:
        fid=save_farm({"name":name.strip() or "My field","place":selected["name"],"latitude":selected["latitude"],"longitude":selected["longitude"],"crop":crop,"soil":soil,"irrigation_method":method,"area_acres":area,"sowing_date":sowing.isoformat(),"harvest_date":harvest.isoformat() if harvest else None}); st.session_state["farm_id"]=fid; st.success("Field saved. Next, open Today’s advice.")
        st.page_link("pages/2_Dashboard.py",label="Go to today's advice",icon="✅")
    except Exception: st.error("Could not save this field. Check the dates and details, then try again.")
farms=list_farms()
if farms:
    st.markdown("### Saved fields")
else:
    st.info("No fields saved yet. Fill in the details above, then choose ‘Save field and continue.’")
for farm in farms:
    col1,col2,col3=st.columns([4,1,1])
    col1.write(f"**{farm['name']}** · {farm['place']} · {farm['crop']} · {farm['area_acres']} acres")
    if col2.button("Select",key=f"use{farm['id']}"):
        st.session_state["farm_id"]=farm["id"]
        st.success(f"Selected {farm['name']}.")
    if col3.button("Delete",key=f"delete{farm['id']}"):
        delete_farm(farm['id'])
        st.rerun()
