import streamlit as st
import google.generativeai as genai
import json

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Trophi.ai Strategy Agent", page_icon="🧠", layout="centered")

# --- STYLING ---
st.markdown("""<style>.stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }</style>""", unsafe_allow_html=True)

# --- HEADER ---
st.title("🧠 Trophi.ai Strategy Agent")
st.caption("Enter a Game or Company. The AI will analyze the Technical & Business viability.")
st.divider()

# --- INPUT SECTION ---
col_input, col_btn = st.columns([3, 1])
with col_input:
    target_name = st.text_input("Target Name", placeholder="e.g. Call of Duty, Logitech, F1 24")
with col_btn:
    st.write("") 
    analyze_btn = st.button("Run Analysis", type="primary")

# --- SESSION STATE ---
if "analysis_done" not in st.session_state: st.session_state.analysis_done = False
if "ai_data" not in st.session_state: st.session_state.ai_data = None

# --- HELPER: GET WORKING MODEL ---
def get_working_model():
    """Selects a model confirmed to be available on your server."""
    # Based on your diagnostic logs, these are the valid models:
    try:
        return genai.GenerativeModel('gemini-2.5-flash')
    except:
        try:
            return genai.GenerativeModel('gemini-flash-latest')
        except:
            # Absolute fallback
            return genai.GenerativeModel('gemini-2.0-flash')

# --- AI LOGIC ---
if analyze_btn and target_name:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        st.error("⚠️ Missing API Key in Secrets.")
