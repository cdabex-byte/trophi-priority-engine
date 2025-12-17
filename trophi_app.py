import streamlit as st
import pandas as pd
import google.generativeai as genai

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Trophi.ai Priority Engine",
    page_icon="🏎️",
    layout="centered"
)

# --- HEADER ---
st.title("🏎️ Trophi.ai Priority Engine")
st.markdown("""
**Strategic Decision Prototype** | Built by David Battcock
*Objective: Quantify 'Opportunity Cost' for Inbound Partnerships & Expansions.*
""")
st.caption("Powered by Google Gemini 1.5 Flash")
st.divider()

# --- SIDEBAR: INPUTS ---
st.sidebar.header("Opportunity Details")
opp_name = st.sidebar.text_input("Project Name", "e.g., Counter-Strike 2 Integration")
opp_type = st.sidebar.selectbox(
    "Opportunity Type", 
    ["New Game Integration", "Hardware Partnership", "Enterprise SDK", "Marketing Event"]
)

st.sidebar.subheader("Scoring Parameters")
st.sidebar.caption("Rate on a scale of 1 (Low) to 5 (High)")

# Sliders
tam_score = st.sidebar.slider("TAM / User Reach", 1, 5, 4, help="How big is the addressable audience?")
rev_potential = st.sidebar.slider("Immediate ARR Potential", 1, 5, 2, help="Will this generate revenue in Q1?")
strat_fit = st.sidebar.slider("Strategic Moat Alignment", 1, 5, 5, help="Does this build our core IP?")
tech_lift = st.sidebar.slider("Engineering Lift (Risk)", 1, 5, 5, help="1=Easy API, 5=Computer Vision/Hard")

# --- THE OPERATOR LOGIC (ALGORITHM) ---
def calculate_score(tam, lift, rev, strat):
    # The "Trophi Formula":
    # High Tech Lift is a massive penalty (-2.5x multiplier)
    # Revenue is King for Series A (+2.0x multiplier)
    
    raw_score = (tam * 1.5) + (rev * 2.0) + (strat * 1.5) - (lift * 2.5)
    
    # Normalize to a 0-100 scale
    # (Based on min/max possible values to ensure spread)
    normalized = max(0, min(100, (raw_score + 10) * 4)) 
    return round(normalized, 1)

final_score = calculate_score(tam_score, tech_lift, rev_potential, strat_fit)

# --- DASHBOARD UI ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"Analysis: {opp_name}")
    
    # Dynamic Logic for Visual Feedback
    if final_score >= 75:
        st.success(f"✅ **GREENLIGHT** (Score: {final_score})")
        st.write("**Strategy:** High ROI. Prioritize implementation immediately.")
    elif final_score >= 50:
        st.warning(f"⚠️ **EVALUATE** (Score: {final_score})")
        st.write("**Strategy:** Move to Backlog. Requires detailed scoping.")
    else:
        st.error(f"🛑 **KILL / DEFER** (Score: {final_score})")
        st.write("**Strategy:** Opportunity Cost is too high. Distraction risk.")

with col2:
    st.metric(label="Trophi Score", value=final_score, delta=f"{'High Risk' if tech_lift > 3 else 'Low Risk'}", delta_color="inverse")

# --- AI GENERATION SECTION ---
st.divider()
st.subheader("🤖 AI Decision Memo Generator")
st.caption("Generates a strategic brief for the CEO based on the parameters above.")

# Check for API Key
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.warning("⚠️ Waiting for API Key in Streamlit Secrets...")

if st.button("Generate Strategy Memo"):
    if "GEMINI_API_KEY" not in st.secrets:
        st.error("Please add GEMINI_API_KEY to your Secrets to enable AI features.")
        st.stop()
    
    with st.spinner("Consulting the Strategy Engine..."):
        
        # 1. SYSTEM INSTRUCTION (The Persona)
        # This forces the AI to act like a Senior Operator, not a chatbot.
        sys_instruction = """
        ROLE:
        You are the Head of Strategy & Operations at Trophi AI. 
        Trophi is a Series A startup ($12M raised from a16z) focused on AI coaching for gamers.
        Your goal is ruthless prioritization. You protect the Engineering Team from distraction.
        
        OPERATIONAL FRAMEWORK:
        1. Opportunity Cost is the enemy. Every hour on a low-ROI project is a loss.
        2. Engineering Lift = Risk. High lift (4/5 or 5/5) requires massive revenue to justify.
        3. Tone: Direct, concise, "Bourdain-esque". No corporate fluff.
        
        OUTPUT FORMAT:
        Produce a "Decision Memo" with these headers:
        
        **VERDICT:** [GREENLIGHT / EVALUATE / KILL] (Based strictly on the Score provided)
        
        **EXECUTIVE SUMMARY:** 
        2 sentences on the "Why".
        
        **RISK ANALYSIS:**
        Bullet points focusing on Technical Debt and Resource Drain.
        
        **RECOMMENDED ACTION:**
        Specific next step (e.g. "Assign 1 PM to scope" or "Send rejection email").
        """

        # 2. INITIALIZE MODEL
        model = genai.GenerativeModel(
            'gemini-1.5-flash',
            system_instruction=sys_instruction
        )
        
        # 3. USER PROMPT (The Data)
        user_prompt = f"""
        Analyze this opportunity:
        Project: "{opp_name}"
        Type: {opp_type}
        
        DATA METRICS:
        - Internal Priority Score: {final_score}/100
        - Strategic Fit: {strat_fit}/5
        - Engineering Lift (Cost): {tech_lift}/5
        - Revenue Potential (ARR): {rev_potential}/5
        """
        
        try:
            # Generate Response
            response = model.generate_content(user_prompt)
            st.markdown(response.text)
        except Exception as e:
            st.error(f"AI Error: {e}")
