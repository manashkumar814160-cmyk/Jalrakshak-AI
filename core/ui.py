import streamlit as st
from pathlib import Path
from .config import ROOT
from .config import DISCLAIMER

def apply_css():
    css=(ROOT/"assets"/"styles.css").read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>",unsafe_allow_html=True)

def banner(message,kind="info"):
    getattr(st,kind if kind in ("info","warning","success","error") else "info")(message)
def disclaimer(): st.caption(DISCLAIMER)
def page_header(title,subtitle=None):
    st.title(title)
    if subtitle: st.write(subtitle)
def metric_card(label,value,help=None): st.metric(label,value,help=help)
