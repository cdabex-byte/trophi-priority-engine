import streamlit as st
import json
import time
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
    .error-box { background-color: #ffebee; padding: 10px; border-radius: 5px; border-left: 5px solid #f44336; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("🧠 Trophi.ai Strategy Agent")
st.caption("Powered by Mistral-7B-Instruct-v0.3 (Hugging Face)")
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
    if "HF_API_TOKEN" in st.secrets:
        client = InferenceClient(token=st.secrets["HF_API_TOKEN"])
    else:
        st.error("❌ Missing 'HF_API_TOKEN' in Streamlit Secrets.")
        st.stop()

    with st.spinner(f"🔍 Analyzing {target_name}..."):
        try:
            # 2. MODEL CONFIGURATION - Mistral-7B-Instruct-v0.3
            MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.3"
            
            # 3. PROMPT FORMATTING - Mistral uses [INST] tags for instruction following
            data_prompt = f"""[INST] You are the Head of Strategy for Trophi AI.
Analyze this target: "{target_name}"

CONTEXT:
- We prefer Games with open APIs (UDP Telemetry) = Low Tech Lift (1/5).
- We dislike Games with kernel Anti-Cheat (requires Computer Vision) = High Tech Lift (5/5).
- We love Hardware partnerships = Zero Tech Lift (1/5).

TASK: Return ONLY a valid JSON object with these exact keys:
{{
    "type": "Game Integration" or "Hardware Partnership",
    "tam_score": Integer 1-5,
    "tech_lift": Integer 1-5,
    "rev_score": Integer 1-5,
    "strat_fit": Integer 1-5,
    "technical_reasoning": "One short sentence"
}}

RULES: Return raw JSON only. No markdown, no extra text, no explanations. [/INST]"""
            
            # 4. CALL API - Using chat_completion for Mistral
            response = client.chat_completion(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": data_prompt}],
                max_tokens=300,
                temperature=0.3,  # Low for consistent JSON output
                top_p=0.9,
            )
            
            # 5. PARSE RESPONSE
            text_data = response.choices[0].message.content
            
            # Mistral sometimes wraps JSON in markdown - clean it aggressively
            text_data = text_data.strip()
            for pattern in ["```json", "```", "[/INST]"]:
                if pattern in text_data:
                    text_data = text_data.replace(pattern, "").strip()
            
            # Remove any trailing text after JSON object
            if "}" in text_data:
                text_data = text_data[:text_data.rfind("}") + 1]
            
            ai_data = json.loads(text_data)
            
            # 6. VALIDATE & CALCULATE
            required_keys = ["type", "tam_score", "tech_lift", "rev_score", "strat_fit", "technical_reasoning"]
            if not all(key in ai_data for key in required_keys):
                st.error("❌ Incomplete response from model")
                st.json(ai_data)
                st.stop()
            
            # Calculate final score
            raw_score = (ai_data['tam_score'] * 1.5) + (ai_data['rev_score'] * 2.0) + (ai_data['strat_fit'] * 1.5) - (ai_data['tech_lift'] * 2.5)
            ai_data['final_score'] = round(max(0, min(100, (raw_score + 10) * 4)), 1)
            
            # 7. SAVE TO STATE
            st.session_state.ai_data = ai_data
            st.session_state.analysis_done = True
            
        except json.JSONDecodeError as e:
            st.error("❌ Could not parse JSON response from Mistral")
            with st.expander("Debug: Raw Response"):
                st.code(text_data[:500])
            st.info("💡 Tip: Try again or switch to a smaller model like 'meta-llama/Llama-3.2-1B-Instruct'")
            
        except Exception as e:
            error_str = str(e).lower()
            if "model_not_supported" in error_str:
                st.error(f"❌ Model '{MODEL_NAME}' not available on Inference API")
                st.info("💡 Check model availability at https://huggingface.co/{MODEL_NAME}")
            elif "429" in error_str or "rate limit" in error_str:
                st.warning("⚠️ Hugging Face rate limit reached")
                st.info("💡 Wait 60 seconds or upgrade to a paid Inference Endpoint")
            elif "401" in error_str:
                st.error("❌ Invalid HF_API_TOKEN")
                st.info("💡 Check your token at https://huggingface.co/settings/tokens")
            else:
                st.error(f"❌ Analysis Error: {e}")
                st.info("💡 Try running again or check the raw response below")
                with st.expander("See full error"):
                    st.code(str(e))

# --- DISPLAY RESULTS ---
if st.session_state.analysis_done and st.session_state.ai_data:
    data = st.session_state.ai_data
    
    st.subheader(f"Analysis: {target_name}")
    st.caption(f"Category: {data['type']}")
    
    # Display metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Trophi Score", data['final_score'], 
              delta="Pass" if data['final_score'] > 60 else "Risk")
    m2.metric("Tech Lift (Risk)", f"{data['tech_lift']}/5", 
              delta_color="inverse", help="1=Easy API, 5=Computer Vision")
    m3.metric("Strategic Fit", f"{data['strat_fit']}/5")
    
    # Technical insight
    st.info(f"💡 **Technical Insight:** {data['technical_reasoning']}")
    
    # Visual sliders
    with st.expander("See Underlying Metrics"):
        st.slider("TAM / Reach", 1, 5, int(data['tam_score']), disabled=True)
        st.slider("Revenue Potential", 1, 5, int(data['rev_score']), disabled=True)
        st.slider("Tech Lift (Cost)", 1, 5, int(data['tech_lift']), disabled=True)

    st.divider()
    st.subheader("📝 Strategic Decision Memo")
    
    if st.button("Draft Executive Brief"):
        with st.spinner("Drafting memo..."):
            try:
                # Memo prompt for Mistral
                memo_prompt = f"""[INST] ROLE: Head of Strategy at Trophi AI.
TASK: Write a decision memo for "{target_name}".
DATA: Score: {data['final_score']}/100, Tech Lift: {data['tech_lift']}/5 ({data['technical_reasoning']})
Verdict: {'GREENLIGHT' if data['final_score'] > 75 else 'EVALUATE' if data['final_score'] > 50 else 'KILL'}

FORMAT:
**VERDICT:** [VERDICT]
**THE BUILD:** Explain engineering reality (APIs vs Computer Vision).
**THE BUSINESS:** Explain ROI.
**RECOMMENDATION:** One clear next step.

Keep it concise and professional. [/INST]"""
                
                memo_response = client.chat_completion(
                    model=MODEL_NAME,
                    messages=[{"role": "user", "content": memo_prompt}],
                    max_tokens=600,
                    temperature=0.5,
                )
                
                st.markdown(memo_response.choices[0].message.content)
                
            except Exception as e:
                st.error(f"❌ Memo Generation Error: {e}")
                st.info("💡 Try running the analysis again first")

# --- FOOTER ---
st.divider()
st.caption("App using Hugging Face Inference API | Model: mistralai/Mistral-7B-Instruct-v0.3")
