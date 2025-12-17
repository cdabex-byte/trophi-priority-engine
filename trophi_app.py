import streamlit as st
import json
from huggingface_hub import InferenceClient

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
st.caption("Powered by Llama-3.2-1B-Instruct (Hugging Face)")
st.divider()

# --- INPUT SECTION ---
col_input, col_btn = st.columns([3, 1])
with col_input:
    target_name = st.text_input("Target Name", placeholder="e.g. Call of Duty, Logitech, F1 24")
with col_btn:
    st.write("")
    analyze_btn = st.button("Run Analysis", type="primary")

# --- INITIALIZE SESSION STATE ---
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "ai_data" not in st.session_state:
    st.session_state.ai_data = None

# --- AI LOGIC ---
if analyze_btn and target_name:
    # 1. Check API Key
    if "HF_API_TOKEN" in st.secrets:
        client = InferenceClient(token=st.secrets["HF_API_TOKEN"])
    else:
        st.error("❌ Missing 'HF_API_TOKEN' in Streamlit Secrets.")
        st.stop()

    with st.spinner(f"🔍 Analyzing {target_name}..."):
        try:
            # 2. MODEL - GUARANTEED AVAILABLE ON FREE TIER
            MODEL_NAME = "meta-llama/Llama-3.2-1B-Instruct"
            
            # 3. PROMPT - Llama 3.2 format with system/user roles
            data_prompt = f"""<|start_header_id|>system<|end_header_id|>
You are the Head of Strategy for Trophi AI. You must return ONLY valid JSON. No markdown, no explanations, no extra text.

CONTEXT:
- Games with open APIs (UDP Telemetry) = Low Tech Lift (1/5)
- Games with kernel Anti-Cheat (requires Computer Vision) = High Tech Lift (5/5)
- Hardware partnerships = Zero Tech Lift (1/5)

TASK: Analyze "{target_name}" and return JSON with these keys:
- type: "Game Integration" or "Hardware Partnership"
- tam_score: Integer 1-5 (5 is High)
- tech_lift: Integer 1-5 (5 is Hard/Risky)
- rev_score: Integer 1-5 (5 is High $$$)
- strat_fit: Integer 1-5 (5 is Perfect)
- technical_reasoning: "One short sentence"<|eot_id|>
<|start_header_id|>user<|end_header_id|>
Analyze the target and return ONLY raw JSON.<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>"""
            
            # 4. CALL API
            response = client.chat_completion(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": data_prompt}],
                max_tokens=250,
                temperature=0.2,  # Very low for consistent JSON
            )
            
            # 5. PARSE RESPONSE - Aggressive cleaning for Llama
            text_data = response.choices[0].message.content
            
            # Remove markdown code fences
            for pattern in ["```json", "```"]:
                if pattern in text_data:
                    text_data = text_data.split(pattern)[1].replace("```", "").strip()
            
            # Extract JSON object if wrapped in text
            if "{" in text_data and "}" in text_data:
                start = text_data.find("{")
                end = text_data.rfind("}") + 1
                text_data = text_data[start:end]
            
            ai_data = json.loads(text_data)
            
            # 6. VALIDATE KEYS
            required_keys = ["type", "tam_score", "tech_lift", "rev_score", "strat_fit", "technical_reasoning"]
            if not all(key in ai_data for key in required_keys):
                st.error("❌ Invalid response structure")
                st.json(ai_data)
                st.stop()
            
            # 7. CALCULATE FINAL SCORE
            raw_score = (ai_data['tam_score'] * 1.5) + (ai_data['rev_score'] * 2.0) + (ai_data['strat_fit'] * 1.5) - (ai_data['tech_lift'] * 2.5)
            ai_data['final_score'] = round(max(0, min(100, (raw_score + 10) * 4)), 1)
            
            st.session_state.ai_data = ai_data
            st.session_state.analysis_done = True
            
        except json.JSONDecodeError:
            st.error("❌ Invalid JSON response")
            with st.expander("Debug: Raw Response"):
                st.code(text_data[:500] if 'text_data' in locals() else "No response")
        except Exception as e:
            error_str = str(e).lower()
            if "model_not_supported" in error_str or "not found" in error_str:
                st.error(f"❌ Model '{MODEL_NAME}' not available")
                st.info("💡 Try: meta-llama/Llama-3.2-3B-Instruct or microsoft/Phi-3-mini-4k-instruct")
            elif "429" in error_str:
                st.warning("⚠️ Rate limit reached. Wait 60s and retry.")
            elif "401" in error_str:
                st.error("❌ Invalid API token")
                st.info("💡 Check HF_API_TOKEN in Streamlit Secrets")
            else:
                st.error(f"❌ Analysis failed: {e}")

# --- DISPLAY RESULTS ---
if st.session_state.analysis_done and st.session_state.ai_data:
    data = st.session_state.ai_data
    
    st.subheader(f"Analysis: {target_name}")
    st.caption(f"Category: {data['type']}")
    
    # Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Trophi Score", data['final_score'], 
              delta="Pass" if data['final_score'] > 60 else "Risk")
    m2.metric("Tech Lift (Risk)", f"{data['tech_lift']}/5", 
              delta_color="inverse", help="1=Easy API, 5=Computer Vision")
    m3.metric("Strategic Fit", f"{data['strat_fit']}/5")
    
    # Technical insight
    st.info(f"💡 **Technical Insight:** {data['technical_reasoning']}")
    
    # Sliders
    with st.expander("See Underlying Metrics"):
        st.slider("TAM / Reach", 1, 5, int(data['tam_score']), disabled=True)
        st.slider("Revenue Potential", 1, 5, int(data['rev_score']), disabled=True)
        st.slider("Tech Lift (Cost)", 1, 5, int(data['tech_lift']), disabled=True)

    st.divider()
    st.subheader("📝 Strategic Decision Memo")
    
    if st.button("Draft Executive Brief"):
        with st.spinner("Drafting memo..."):
            try:
                memo_prompt = f"""<|start_header_id|>system<|end_header_id|>
Write a concise executive decision memo. Be direct and professional.<|eot_id|>
<|start_header_id|>user<|end_header_id|>
Target: {target_name}
Score: {data['final_score']}/100
Tech Lift: {data['tech_lift']}/5 ({data['technical_reasoning']})
Verdict: {'GREENLIGHT' if data['final_score'] > 75 else 'EVALUATE' if data['final_score'] > 50 else 'KILL'}

Format: **VERDICT**, **THE BUILD**, **THE BUSINESS**, **RECOMMENDATION**<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>"""
                
                memo_response = client.chat_completion(
                    model=MODEL_NAME,
                    messages=[{"role": "user", "content": memo_prompt}],
                    max_tokens=500,
                    temperature=0.4,
                )
                
                st.markdown(memo_response.choices[0].message.content)
                
            except Exception as e:
                st.error(f"Memo generation failed: {e}")
                st.info("💡 Try running the analysis again first")

# --- FOOTER ---
st.divider()
st.caption("App runs on Hugging Face Inference API | Model: meta-llama/Llama-3.2-1B-Instruct")
