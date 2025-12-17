import streamlit as st
import google.generativeai as genai
import json
import time

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
st.caption("Powered by Gemini 2.0 Flash (High Speed)")
st.divider()

# --- INPUT SECTION ---
col_input, col_btn = st.columns([3, 1])
with col_input:
    target_name = st.text_input("Target Name", placeholder="e.g. Call of Duty, Logitech, F1 24")
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
    # 1. Check API Key
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        st.error("❌ Missing 'GEMINI_API_KEY' in Streamlit Secrets.")
        st.stop()

    with st.spinner(f"🔍 Analyzing {target_name}..."):
        try:
            # 2. USE GEMINI 2.0 FLASH (Best for Free Tier Quotas)
            # Based on your logs, this model is available and has higher limits
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            # 3. DEFINE PROMPT
            data_prompt = f"""
            Act as the Head of Strategy for Trophi AI.
            Analyze this target: "{target_name}"
            
            CONTEXT:
            - We prefer Games with open APIs (UDP Telemetry) = Low Tech Lift (1/5).
            - We dislike Games with kernel Anti-Cheat (requires Computer Vision) = High Tech Lift (5/5).
            - We love Hardware partnerships = Zero Tech Lift (1/5).
            
            TASK:
            Return a JSON object with estimates.
            RULES: Return ONLY raw JSON. Do not write "Here is the JSON".
            
            {{
                "type": "Game Integration" or "Hardware Partnership",
                "tam_score": (Integer 1-5, 5 is High),
                "tech_lift": (Integer 1-5, 5 is Hard/Risky),
                "rev_score": (Integer 1-5, 5 is High $$$),
                "strat_fit": (Integer 1-5, 5 is Perfect),
                "technical_reasoning": "One short sentence explaining the Tech Lift score"
            }}
            """
            
            # 4. CALL API
            response = model.generate_content(data_prompt)
            
            # 5. PARSE RESPONSE
            text_data = response.text
            # Clean up markdown if the AI adds it
            if "```json" in text_data:
                text_data = text_data.split("```json")[1].split("```")[0]
            elif "```" in text_data:
                text_data = text_data.replace("```", "")
            
            ai_data = json.loads(text_data.strip())
            
            # 6. CALCULATE SCORE
            raw_score = (ai_data['tam_score'] * 1.5) + (ai_data['rev_score'] * 2.0) + (ai_data['strat_fit'] * 1.5) - (ai_data['tech_lift'] * 2.5)
            ai_data['final_score'] = round(max(0, min(100, (raw_score + 10) * 4)), 1)
            
            # 7. SAVE TO STATE
            st.session_state.ai_data = ai_data
            st.session_state.analysis_done = True
            
        except Exception as e:
            # Handle Quota Errors Gracefully
            if "429" in str(e):
                st.warning("⚠️ High Traffic: API Quota Exceeded. Please wait 60 seconds and try again.")
            else:
                st.error(f"❌ Analysis Error: {e}")

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
    
    # Sliders for visual context
    with st.expander("See Underlying Metrics"):
        st.slider("TAM / Reach", 1, 5, int(data['tam_score']), disabled=True)
        st.slider("Revenue Potential", 1, 5, int(data['rev_score']), disabled=True)
        st.slider("Tech Lift (Cost)", 1, 5, int(data['tech_lift']), disabled=True)

    st.divider()
    st.subheader("📝 Strategic Decision Memo")
    
    if st.button("Draft Executive Brief"):
        with st.spinner("Drafting memo..."):
            try:
                model = genai.GenerativeModel('gemini-2.0-flash')
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
            except Exception as e:
                st.error(f"Memo Generation Error: {e}")
