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
    """Finds a model that actually exists on this server."""
    try:
        # Try the modern flash model first
        return genai.GenerativeModel('gemini-1.5-flash')
    except:
        try:
            # Fallback to Pro
            return genai.GenerativeModel('gemini-pro')
        except:
            # Fallback to 1.0
            return genai.GenerativeModel('gemini-1.0-pro')

# --- AI LOGIC ---
if analyze_btn and target_name:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        st.error("⚠️ Missing API Key in Secrets.")
        st.stop()

    with st.spinner(f"🔍 Deconstructing {target_name}..."):
        try:
            # 1. FIND A MODEL THAT WORKS
            model = get_working_model()
            
            # 2. RUN ANALYSIS
            data_prompt = f"""
            Act as the CTO and Head of Strategy for Trophi AI.
            Analyze this target: "{target_name}"
            
            CONTEXT:
            - We prefer Games with open APIs (UDP Telemetry) (Low Risk).
            - We dislike Games with kernel Anti-Cheat that need Computer Vision (High Risk).
            - We love Hardware partnerships.
            
            TASK:
            Return valid JSON with these estimates (1-5 Scale).
            OUTPUT JSON FORMAT ONLY. NO MARKDOWN.
            {{
                "type": "Game Integration" or "Hardware Partnership",
                "tam_score": (Integer 1-5),
                "tech_lift": (Integer 1-5, 5=Hard/CV),
                "rev_score": (Integer 1-5),
                "strat_fit": (Integer 1-5),
                "technical_reasoning": "Short explanation of the Tech Lift score"
            }}
            """
            
            response = model.generate_content(data_prompt)
            
            # CLEAN JSON
            text_data = response.text
            if "```json" in text_data:
                text_data = text_data.split("```json")[1].split("```")[0]
            elif "```" in text_data:
                text_data = text_data.replace("```", "")
            
            ai_data = json.loads(text_data.strip())
            
            # SCORING MATH
            raw_score = (ai_data['tam_score'] * 1.5) + (ai_data['rev_score'] * 2.0) + (ai_data['strat_fit'] * 1.5) - (ai_data['tech_lift'] * 2.5)
            ai_data['final_score'] = round(max(0, min(100, (raw_score + 10) * 4)), 1)
            
            st.session_state.ai_data = ai_data
            st.session_state.analysis_done = True
            
        except Exception as e:
            st.error(f"Analysis Failed: {e}")
            # DIAGNOSTIC INFO IF IT FAILS
            try:
                st.write("Available Models on this Server:")
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        st.code(m.name)
            except:
                st.write("Could not list models. Check API Key.")

# --- DISPLAY RESULTS ---
if st.session_state.analysis_done and st.session_state.ai_data:
    data = st.session_state.ai_data
    
    st.subheader(f"Analysis: {target_name}")
    st.caption(f"Category: {data['type']}")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Trophi Score", data['final_score'], delta="Pass" if data['final_score'] > 60 else "Risk")
    m2.metric("Tech Lift (Risk)", f"{data['tech_lift']}/5", delta_color="inverse")
    m3.metric("Strategic Fit", f"{data['strat_fit']}/5")
    
    st.info(f"💡 **Technical Insight:** {data['technical_reasoning']}")
    
    st.divider()
    
    if st.button("Draft Executive Brief"):
        with st.spinner("Drafting memo..."):
            model = get_working_model()
            memo_prompt = f"""
            ROLE: Head of Strategy at Trophi AI.
            TASK: Write a decision memo for "{target_name}".
            DATA: Score: {data['final_score']}/100, Tech Lift: {data['tech_lift']}/5.
            FORMAT:
            **VERDICT:** [GREENLIGHT/KILL]
            **THE BUILD:** Engineering reality.
            **RECOMMENDATION:** Next step.
            """
            memo_res = model.generate_content(memo_prompt)
            st.markdown(memo_res.text)
