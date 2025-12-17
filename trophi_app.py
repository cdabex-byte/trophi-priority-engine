import streamlit as st
import json
from huggingface_hub import InferenceClient

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Trophi.ai Strategy Agent",
    page_icon="🧠",
    layout="centered"
)

# --- STYLING - Fixed contrast issues ---
st.markdown("""
    <style>
    .big-font { font-size:20px !important; }
    .stMetric {
        background-color: #f0f2f6 !important;
        padding: 10px;
        border-radius: 10px;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #1f1f1f !important;  /* Dark text for metric values */
    }
    .stMetric [data-testid="stMetric
