import streamlit as st
import google.generativeai as genai
import json

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Trophi.ai Strategy Agent",
    page_icon="🧠",
    layout="centered"
)

# --- STYLING ---
st.markdown("""
    <style>
    .big-font { font-size:20px !important; }
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("🧠 Trophi.ai Strategy Agent")
st.caption("Enter a Game or Company. The AI will analyze the Technical & Business viability.")
st.divider()

# --- INPUT SECTION ---
col_input, col_btn = st.columns([3, 1])
with col_input:
    target_name = st.text_input("Target Name", placeholder="e.g. Valorant, Logitech, F1 24")
with col_btn:
    st.write("") # Spacer
    analyze_btn = st.button("Run Analysis", type="primary")

# --- INITIALIZE SESSION STATE ---
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "ai_data" not in st.session_state:
    st.session_state.ai_data = None

# --- AI LOGIC ---
if analyze_btn and target_name:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        st.error("⚠️ Missing API Key in Secrets.")
        st.stop()

    with st.spinner(f"🔍 Deconstructing {target_name}..."):
        try:
            # USE GEMINI 1.5 FLASH (Standard, Fast, Free)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # --- PROMPT 1: THE DATA ESTIMATOR ---
            data_prompt = f"""
            Act as the CTO and Head of Strategy for Trophi AI.
            Analyze this target: "{target_name}"
            
            CONTEXT:
            - We prefer Games with open APIs (UDP Telemetry) (Low Risk).
            - We dislike Games with kernel Anti-Cheat that need Computer Vision (High Risk).
            - We love Hardware partnerships.
            
            TASK:
            Return valid JSON with these estimates (1-5 Scale):
            
            OUTPUT JSON FORMAT ONLY:
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
            
            # Clean JSON (Strip markdown formatting if AI adds it)
            cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
            ai_data = json.loads(cleaned_text)
            
            # Calculate Trophi Score
            raw_score = (ai_data['tam_score'] * 1.5) + (ai_data['rev_score'] * 2.0) + (ai_data['strat_fit'] * 1.5) - (ai_data['tech_lift'] * 2.5)
            # Normalize logic
            ai_data['final_score'] = round(max(0, min(100, (raw_score + 10) * 4)), 1)
            
            st.session_state.ai_data = ai_data
            st.session_state.analysis_done = True
            
        except Exception as e:
            st.error(f"Analysis Failed: {e}")
            st.warning("Tip: Try clicking 'Run Analysis' again, or check your API Key.")

# --- DISPLAY RESULTS ---
if st.session_state.analysis_done and st.session_state.ai_data:
    data = st.session_state.ai_data
    
    st.subheader(f"Analysis: {target_name}")
    st.caption(f"Category: {data['type']}")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Trophi Score", data['final_score'], delta="Pass" if data['final_score'] > 60 else "Risk")
    m2.metric("Tech Lift (Risk)", f"{data['tech_lift']}/5", delta_color="inverse", help="1=Easy API, 5=Computer Vision")
    m3.metric("Strategic Fit", f"{data['strat_fit']}/5")
    
    st.info(f"💡 **Technical Insight:** {data['technical_reasoning']}")
    
    with st.expander("See Underlying Metrics"):
        st.slider("TAM / Reach", 1, 5, int(data['tam_score']), disabled=True)
        st.slider("Revenue Potential", 1, 5, int(data['rev_score']), disabled=True)
        st.slider("Strategic Fit", 1, 5, int(data['strat_fit']), disabled=True)
        st.slider("Tech Lift (Cost)", 1, 5, int(data['tech_lift']), disabled=True)

    st.divider()
    st.subheader("📝 Strategic Decision Memo")
    
    if st.button("Draft Executive Brief"):
        with st.spinner("Drafting memo..."):
            model = genai.GenerativeModel('gemini-1.5-flash')
            memo_prompt = f"""
            ROLE: Head of Strategy at Trophi AI.
            TASK: Write a decision memo for "{target_name}".
            DATA: 
            - Score: {data['final_score']}/100
            - Tech Lift: {data['tech_lift']}/5 ({data['technical_reasoning']})
            - Verdict: {'GREENLIGHT' if data['final_score'] > 75 else 'EVALUATE' if data['final_score'] > 50 else 'KILL'}
            
            FORMAT:
            **VERDICT:** [VERDICT]
            **THE BUILD:** Explain the engineering reality (mention APIs vs Computer Vision).
            **THE BUSINESS:** Explain the ROI.
            **RECOMMENDATION:** One clear next step.
            """
            memo_res = model.generate_content(memo_prompt)
            st.markdown(memo_res.text)
