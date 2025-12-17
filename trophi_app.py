import streamlit as st
import json
import time
from huggingface_hub import InferenceClient  # NEW IMPORT

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
st.caption("Powered by Hugging Face Inference API (Free Tier)")
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
            # 2. CHOOSE MODEL - Optimized for JSON output
            # Recommended free models (in order of preference):
            # - "microsoft/Phi-3-mini-4k-instruct" (fast, excellent JSON)
            # - "meta-llama/Llama-3.2-1B-Instruct" (smallest, fastest)
            # - "mistralai/Mistral-7B-Instruct-v0.3" (more capable, slightly slower)
            
            model_name = "microsoft/Phi-3-mini-4k-instruct"  # <-- You can change this
            
            # 3. DEFINE PROMPT - Enhanced for better JSON compliance
            data_prompt = f"""You are the Head of Strategy for Trophi AI. Analyze this target: "{target_name}"

CONTEXT:
- We prefer Games with open APIs (UDP Telemetry) = Low Tech Lift (1/5).
- We dislike Games with kernel Anti-Cheat (requires Computer Vision) = High Tech Lift (5/5).
- We love Hardware partnerships = Zero Tech Lift (1/5).

TASK: Return ONLY a valid JSON object with these exact keys:
{{
    "type": "Game Integration" or "Hardware Partnership",
    "tam_score": (Integer 1-5, 5 is High),
    "tech_lift": (Integer 1-5, 5 is Hard/Risky),
    "rev_score": (Integer 1-5, 5 is High $$$),
    "strat_fit": (Integer 1-5, 5 is Perfect),
    "technical_reasoning": "One short sentence explaining the Tech Lift score"
}}

RULES:
- Return ONLY raw JSON, no markdown, no explanations
- Ensure all keys are present and values are valid integers/strings
- Do not include any additional text before or after the JSON
"""
            
            # 4. CALL API - Using chat_completion for better instruction following
            response = client.chat_completion(
                model=model_name,
                messages=[{"role": "user", "content": data_prompt}],
                max_tokens=500,
                temperature=0.3,  # Low temperature for consistent output
            )
            
            # 5. PARSE RESPONSE
            text_data = response.choices[0].message.content
            
            # Clean up any potential markdown wrapping
            if "```json" in text_data:
                text_data = text_data.split("```json")[1].split("```")[0]
            elif "```" in text_data:
                text_data = text_data.replace("```", "")
            
            # Strip any leading/trailing whitespace
            text_data = text_data.strip()
            
            # Parse JSON
            ai_data = json.loads(text_data)
            
            # 6. CALCULATE SCORE (same logic as before)
            raw_score = (ai_data['tam_score'] * 1.5) + (ai_data['rev_score'] * 2.0) + (ai_data['strat_fit'] * 1.5) - (ai_data['tech_lift'] * 2.5)
            ai_data['final_score'] = round(max(0, min(100, (raw_score + 10) * 4)), 1)
            
            # 7. SAVE TO STATE
            st.session_state.ai_data = ai_data
            st.session_state.analysis_done = True
            
        except json.JSONDecodeError as e:
            st.error("❌ Invalid JSON response from model. Try again or switch models.")
            st.info(f"Raw response: {text_data[:200]}...")
        except Exception as e:
            # Handle Hugging Face specific errors
            error_str = str(e)
            if "429" in error_str or "rate limit" in error_str.lower():
                st.warning("⚠️ Hugging Face Rate Limit Reached. Wait 60s or try a smaller model.")
            elif "401" in error_str:
                st.error("❌ Invalid HF_API_TOKEN. Check your Streamlit Secrets.")
            elif "Model not found" in error_str:
                st.error(f"❌ Model '{model_name}' not available. Try another model.")
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
                memo_prompt = f"""ROLE: Head of Strategy at Trophi AI.
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
                
                memo_response = client.chat_completion(
                    model=model_name,
                    messages=[{"role": "user", "content": memo_prompt}],
                    max_tokens=800,
                    temperature=0.5,
                )
                st.markdown(memo_response.choices[0].message.content)
            except Exception as e:
                st.error(f"Memo Generation Error: {e}")
