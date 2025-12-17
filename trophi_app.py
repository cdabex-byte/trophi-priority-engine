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
    .stMetric [data-testid="stMetricLabel"] {
        color: #333333 !important;  /* Dark text for labels */
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("🧠 Trophi.ai Strategy Agent")
st.caption("Powered by Llama-3.2-1B-Instruct (Hugging Face)")
st.divider()

# --- SESSION STATE INITIALIZATION ---
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "ai_data" not in st.session_state:
    st.session_state.ai_data = None
if "memo_text" not in st.session_state:
    st.session_state.memo_text = None

# --- INPUT SECTION ---
col_input, col_btn = st.columns([3, 1])
with col_input:
    target_name = st.text_input("Target Name", placeholder="e.g. Call of Duty, Logitech, F1 24")
with col_btn:
    st.write("")
    analyze_btn = st.button("Run Analysis", type="primary")

# --- ANALYSIS LOGIC ---
if analyze_btn and target_name:
    # 1. Check API Key
    if "HF_API_TOKEN" in st.secrets:
        client = InferenceClient(token=st.secrets["HF_API_TOKEN"])
        st.session_state.client = client  # Store for memo generation
    else:
        st.error("❌ Missing 'HF_API_TOKEN' in Streamlit Secrets.")
        st.stop()

    with st.spinner(f"🔍 Analyzing {target_name}..."):
        try:
            MODEL_NAME = "meta-llama/Llama-3.2-1B-Instruct"
            
            # Analysis prompt
            data_prompt = f"""<|start_header_id|>system<|end_header_id|>
Return ONLY valid JSON. No markdown, no explanations.

Analyze: "{target_name}"
Return keys: type, tam_score, tech_lift, rev_score, strat_fit, technical_reasoning
Context: API=Low Tech(1), AntiCheat=High Tech(5), Hardware=Zero Tech(1)
<|eot_id|><|start_header_id|>user<|end_header_id|>
Analyze and return ONLY raw JSON.<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
            
            response = client.chat_completion(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": data_prompt}],
                max_tokens=250,
                temperature=0.2,
            )
            
            # Parse analysis
            text_data = response.choices[0].message.content
            for pattern in ["```json", "```"]:
                if pattern in text_data:
                    text_data = text_data.split(pattern)[1].replace("```", "").strip()
            
            if "{" in text_data and "}" in text_data:
                text_data = text_data[text_data.find("{"):text_data.rfind("}") + 1]
            
            ai_data = json.loads(text_data)
            
            # Calculate score
            raw_score = (ai_data['tam_score'] * 1.5) + (ai_data['rev_score'] * 2.0) + (ai_data['strat_fit'] * 1.5) - (ai_data['tech_lift'] * 2.5)
            ai_data['final_score'] = round(max(0, min(100, (raw_score + 10) * 4)), 1)
            
            st.session_state.ai_data = ai_data
            st.session_state.analysis_done = True
            
            # --- AUTO-GENERATE MEMO ---
            st.info("📝 Drafting executive brief...")
            
            verdict = 'GREENLIGHT' if ai_data['final_score'] > 75 else 'EVALUATE' if ai_data['final_score'] > 50 else 'KILL'
            
            memo_prompt = f"""<|start_header_id|>system<|end_header_id|>
Write a concise executive decision memo. Be direct and professional.
Format: **VERDICT**, **THE BUILD**, **THE BUSINESS**, **RECOMMENDATION**<|eot_id|>
<|start_header_id|>user<|end_header_id|>
Target: {target_name}
Score: {ai_data['final_score']}/100
Tech Lift: {ai_data['tech_lift']}/5 ({ai_data['technical_reasoning']})
Verdict: {verdict}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
            
            memo_response = client.chat_completion(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": memo_prompt}],
                max_tokens=500,
                temperature=0.4,
            )
            
            st.session_state.memo_text = memo_response.choices[0].message.content
            
        except Exception as e:
            st.error(f"❌ Analysis failed: {e}")
            if 'text_data' in locals():
                with st.expander("Debug: Raw Response"):
                    st.code(text_data[:500])

# --- DISPLAY RESULTS ---
if st.session_state.analysis_done and st.session_state.ai_data:
    data = st.session_state.ai_data
    
    st.subheader(f"Analysis: {target_name}")
    st.caption(f"Category: {data['type']}")
    
    # Metrics with fixed styling
    m1, m2, m3 = st.columns(3)
    m1.metric("Trophi Score", data['final_score'], 
              delta="Pass" if data['final_score'] > 60 else "Risk")
    m2.metric("Tech Lift (Risk)", f"{data['tech_lift']}/5", 
              delta_color="inverse", help="1=Easy API, 5=Computer Vision")
    m3.metric("Strategic Fit", f"{data['strat_fit']}/5")
    
    st.info(f"💡 **Technical Insight:** {data['technical_reasoning']}")
    
    # Sliders
    with st.expander("See Underlying Metrics"):
        st.slider("TAM / Reach", 1, 5, int(data['tam_score']), disabled=True)
        st.slider("Revenue Potential", 1, 5, int(data['rev_score']), disabled=True)
        st.slider("Tech Lift (Cost)", 1, 5, int(data['tech_lift']), disabled=True)

    st.divider()
    st.subheader("📝 Strategic Decision Memo")
    
    # Auto-display memo
    if st.session_state.memo_text:
        st.markdown(st.session_state.memo_text)
    else:
        st.warning("Memo generation in progress...")

# --- FOOTER ---
st.divider()
st.caption("App using Hugging Face Inference API | Model: Llama-3.2-1B-Instruct")
