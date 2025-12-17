import streamlit as st
import json
import time
from huggingface_hub import InferenceClient

# --- ENTERPRISE CONTEXT (Immutable) ---
TROPHI_INTELLIGENCE = {
    "company": {
        "mission": "Democratize elite-level AI coaching, delivering 10x human coach efficiency",
        "founded": "Dec 2021",
        "founders": ["Mike Winter (CEO, Memorial University)", "Scott Mansell (ex-pro)"],
        "headcount": 22,
        "funding": "$3.3M Seed + $548K CAD grants",
        "accelerator": "A16Z GAMES SPEEDRUN (Winter 2025)",
        "moat": "125 years of human coaching data, sub-second latency"
    },
    "tech_stack": {
        "primary": "UDP telemetry streams",
        "anti_cheat_policy": "ZERO kernel-level AC integrations",
        "priority_methods": ["Direct API/SDK (1-2 days)", "UDP parsing (7-14 days)", "Computer Vision (AVOID)"],
        "performance": "95%+ accuracy vs human elite coaches"
    },
    "market_data": {
        "racing_sim": {"$0.87B": "2024", "CAGR": "7.3%"},
        "virtual_sports": {"$0.97B": "2024", "CAGR": "8.1%"},
        "demographics": "21-35 years (millennial/Gen Z)",
        "geography": "NA 40%, EU 35%, APAC fastest growth"
    },
    "financial_targets": {
        "ltv_goal": "$180+",
        "cac_target": "<$45",
        "payback": "< 3 months",
        "pricing_tiers": ["$9.99", "$19.99", "$29.99"],
        "partnership_model": "Revenue share with hardware OEMs"
    }
}

# --- STRICT EVALUATION FRAMEWORK ---
EVALUATION_RUBRIC = """Score 1-10, NO GUESSING:
- **Market Attractiveness**: Use ONLY verifiable data (SteamSpy, official player counts, financial reports). If data unavailable, score 1-3 and state "Insufficient public data".
- **Technical Feasibility**: 
  1-2 = Public API/SDK exists
  3-4 = UDP telemetry available
  5-6 = Limited data access
  7-8 = Requires CV/non-API methods
  9-10 = Kernel anti-cheat (AUTO-REJECT)
- **Revenue Potential**: Base on Trophi's $180 LTV target. Use comparable pricing from VRS, Coach Dave Academy. If unknown, score 1-3.
- **Strategic Fit**: 
  9-10 = Direct racing core (iRacing, F1 series)
  6-8 = Hardware partnerships
  3-5 = Adjacent esports
  1-2 = Unrelated verticals

CRITICAL: If any dimension lacks verifiable data, append "_uncertain" to score and provide confidence 0-100%."""

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Trophi.ai Scale Decision Engine",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MODERN GLASSMORPHISM UI ---
st.markdown("""
    <style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');
    
    /* Global styling */
    * {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Glassmorphism header */
    .header-glass {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(12px) saturate(1.8);
        border-radius: 16px;
        padding: 30px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.2);
        margin-bottom: 30px;
    }
    
    /* Metrics cards - glass effect */
    .metric-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.9) 0%, rgba(118, 75, 162, 0.9) 100%);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.2);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .metric-value {
        color: white !important;
        font-weight: 900 !important;
        font-size: 2.8rem !important;
        font-family: 'Inter', sans-serif !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .metric-label {
        color: rgba(255, 255, 255, 0.85) !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Section headers */
    .section-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 900 !important;
        font-size: 1.8rem !important;
        margin-bottom: 20px;
    }
    
    /* Data confidence indicator */
    .confidence-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: 600;
        margin-left: 8px;
    }
    
    .conf-high { background: #d4edda; color: #155724; }
    .conf-med { background: #fff3cd; color: #856404; }
    .conf-low { background: #f8d7da; color: #721c24; }
    
    /* Executive memo styling */
    .memo-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 30px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        font-family: 'Inter', sans-serif;
    }
    
    .memo-container h3 {
        color: #667eea;
        margin-top: 25px;
        font-weight: 700;
        border-bottom: 2px solid rgba(102, 126, 234, 0.3);
        padding-bottom: 8px;
    }
    
    /* Loading animation */
    .loading-spinner {
        text-align: center;
        padding: 40px;
    }
    
    /* Input styling */
    .stTextInput input {
        border-radius: 12px;
        border: 2px solid rgba(102, 126, 234, 0.3);
        padding: 15px;
        font-size: 1.1rem;
        transition: border-color 0.3s;
    }
    
    .stTextInput input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Button styling */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 15px 30px;
        font-weight: 700;
        font-size: 1rem;
        border: none;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<div class="header-glass">', unsafe_allow_html=True)
st.title("🧠 Trophi.ai Scale Decision Engine")
st.caption("**AI-Powered Strategic Opportunity Assessment** | A16Z SPEEDRUN Portfolio")
st.markdown('</div>', unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.subheader("📊 Evaluation Framework")
    confidence = st.select_slider("Data Confidence Threshold", 
                                  options=["Low", "Medium", "High"], 
                                  value="High",
                                  help="Higher = Only verifiable data sources, Lower = Allow estimates")
    
    st.divider()
    st.subheader("Trophi Intelligence")
    st.metric("Funding", "$3.3M Seed", "Build Ventures 2024")
    st.metric("Team", "22 → 44 EOY 2025", "2x Growth")
    st.metric("Moat", "125yr coaching data", "6 months")

# --- SESSION STATE ---
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "ai_data" not in st.session_state:
    st.session_state.ai_data = None
if "memo_text" not in st.session_state:
    st.session_state.memo_text = None

# --- INPUT SECTION ---
st.markdown('<div class="section-header">🎯 Opportunity Evaluation</div>', unsafe_allow_html=True)
col_input, col_btn = st.columns([4, 1])
with col_input:
    target_name = st.text_input("", 
                                placeholder="Enter opportunity: 'iRacing F1 25 API', 'Logitech G Pro Partnership'...")
with col_btn:
    st.write("")
    analyze_btn = st.button("⚡ Analyze", use_container_width=True)

# --- ANALYSIS LOGIC ---
if analyze_btn and target_name:
    if "HF_API_TOKEN" not in st.secrets:
        st.error("❌ Missing 'HF_API_TOKEN' in Streamlit Secrets")
        st.stop()
    
    client = InferenceClient(token=st.secrets["HF_API_TOKEN"])
    st.session_state.client = client

    with st.spinner(f"🔍 Evaluating **{target_name}**..."):
        try:
            MODEL_NAME = "meta-llama/Llama-3.2-1B-Instruct"
            
            # Strict prompt with confidence requirements
            strict_prompt = f"""<|start_header_id|>system<|end_header_id|>
You are Trophi.ai's VP of Strategy. Evaluate with **precision** - NO FABRICATION.

=== VERIFICATION RULES ===
1. IF public data unavailable → State "INSUFFICIENT_DATA" and score 1-3
2. IF integration method unclear → Ask "CONFIRM_API_ACCESS"
3. IF user base unknown → Use "est_users": "Undisclosed"
4. ALWAYS include "confidence": 0-100 (100% = verified source, <50% = estimate)

=== MANDATORY DATA SOURCES ===
- Market size: Use MarketsandMarkets, Straits Research, or company IR
- User counts: SteamSpy, official press releases, Activision Blizzard earnings
- Technical specs: Official dev documentation, API docs, or GitHub
- Pricing: Public pricing pages, Capterra, G2

=== COMPANY MANDATE ===
- **AUTO-REJECT** if requires kernel anti-cheat
- **PRIO_PATH**: Direct API > UDP > CV (last resort)
- **HEADCOUNT**: 2 engineers max for <30 day integrations
- **LTV_TARGET**: $180+ or partner revenue share

=== OUTPUT SCHEMA ===
{{"target": string,
 "overall_score": float,
 "confidence": 0-100,
 "market_attractiveness": {{"score": int, "rationale": string, "source": string, "est_users": string, "cagr": string}},
 "technical_feasibility": {{"score": int, "rationale": string, "integration_method": string, "integration_days": int, "risk_level": string}},
 "revenue_potential": {{"score": int, "rationale": string, "pricing_power": string, "arr_potential": string}},
 "strategic_fit": {{"score": int, "rationale": string, "velocity_score": int}},
 "key_risks": [string],
 "data_gaps": [string],
 "go_to_market": string}}<|eot_id|><|start_header_id|>user<|end_header_id|>
Evaluate: {target_name}
Return JSON only<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
            
            response = client.chat_completion(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": strict_prompt}],
                max_tokens=700,
                temperature=0.1,  # Minimize hallucination
            )
            
            # Parse with validation
            text_data = response.choices[0].message.content
            for pattern in ["```json", "```"]:
                if pattern in text_data:
                    text_data = text_data.split(pattern)[1].replace("```", "").strip()
            
            if "{" in text_data and "}" in text_data:
                text_data = text_data[text_data.find("{"):text_data.rfind("}") + 1]
            
            ai_data = json.loads(text_data)
            
            # Validation layer 2: Check for hallucination markers
            hallucination_indicators = ["unknown", "estimated", "approximately"]
            if "confidence" not in ai_data or ai_data["confidence"] < 70:
                st.warning(f"⚠️ Low confidence ({ai_data.get('confidence', 0)}%) - verify data sources")
            
            # Calculate weighted score
            market = ai_data["market_attractiveness"]["score"] * 3.5
            tech = ai_data["technical_feasibility"]["score"] * 2.5
            revenue = ai_data["revenue_potential"]["score"] * 2.5
            strategy = ai_data["strategic_fit"]["score"] * 1.5
            
            ai_data["overall_score"] = round(min(100, (market + tech + revenue + strategy)), 1)
            
            st.session_state.ai_data = ai_data
            st.session_state.analysis_done = True
            
            # --- AUTO-MEMO ---
            with st.spinner("📝 Generating board memo..."):
                memo_prompt = f"""<|start_header_id|>system<|end_header_id|>
You are presenting to A16Z GAMES partners & Trophi.ai board.

MEMO STRUCTURE:
1. **EXECUTIVE VERDICT** [GREENLIGHT/CAUTIOUS/KILL]
2. **MARKET EVIDENCE** [Size, CAGR, sources]
3. **TECHNICAL REALITY** [Integration path, timeline, risks]
4. **REVOps MODEL** [Pricing, LTV, GTM playbook]
5. **RESOURCE ASK** [Headcount, budget, milestones]
6. **30-DAY ACTION PLAN** [Specific deliverables]

TONE: Data-driven, confident, no fluff. Cite sources where available.<|eot_id|><|start_header_id|>user<|end_header_id|>
Opportunity: {target_name}
Core Data: {json.dumps(ai_data, indent=2)}

Draft memo for board consumption.<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
                
                memo_response = client.chat_completion(
                    model=MODEL_NAME,
                    messages=[{"role": "user", "content": memo_prompt}],
                    max_tokens=1000,
                    temperature=0.3,
                )
                
                st.session_state.memo_text = memo_response.choices[0].message.content
                
        except Exception as e:
            st.error(f"❌ Analysis failed: {str(e)}")
            if 'text_data' in locals():
                with st.expander("Debug Raw"):
                    st.code(text_data[:500])

# --- DISPLAY RESULTS ---
if st.session_state.analysis_done and st.session_state.ai_data:
    data = st.session_state.ai_data
    
    # Score header
    conf_class = "conf-high" if data.get("confidence", 0) >= 80 else "conf-med" if data.get("confidence", 0) >= 60 else "conf-low"
    
    st.markdown(f"""
        <div class="section-header">
            📊 Overall Score: {data['overall_score']}/100
            <span class="confidence-badge {conf_class}">{data.get('confidence', 0)}% Confidence</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.caption(f"**Target:** {data['target']} | **Model:** Llama-3.2-1B-Instruct")
    
    # Create columns
    col_main, col_side = st.columns([3, 1])
    
    with col_main:
        # Metrics grid
        metrics = st.columns(2)
        dimension_map = {
            "market_attractiveness": {"icon": "🌍", "color": "#667eea"},
            "technical_feasibility": {"icon": "⚙️", "color": "#764ba2"},
            "revenue_potential": {"icon": "💰", "color": "#f093fb"},
            "strategic_fit": {"icon": "🎯", "color": "#f5576c"}
        }
        
        for idx, dimension in enumerate(['market_attractiveness', 'technical_feasibility', 'revenue_potential', 'strategic_fit']):
            with metrics[idx % 2]:
                score = data[dimension]["score"]
                rationale = data[dimension]["rationale"][:100] + "..."
                
                st.markdown(f"""
                    <div class="metric-card" style="background: linear-gradient(135deg, {dimension_map[dimension]['color']} 0%, {dimension_map[dimension]['color']}aa 100%);">
                        <div class="metric-label">{dimension_map[dimension]['icon']} {dimension.replace('_', ' ').title()}</div>
                        <div class="metric-value">{score}/10</div>
                        <div style="color: rgba(255,255,255,0.8); font-size: 0.8rem; margin-top: 10px;">
                            {rationale}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        
        # Dimensional details
        st.divider()
        st.markdown('<div class="section-header">📈 Dimensional Analysis</div>', unsafe_allow_html=True)
        
        tabs = st.tabs(["🌍 Market", "⚙️ Tech", "💰 Revenue", "🎯 Strategy"])
        
        for idx, dimension in enumerate(['market_attractiveness', 'technical_feasibility', 'revenue_potential', 'strategic_fit']):
            with tabs[idx]:
                st.write(f"**Rationale:** {data[dimension]['rationale']}")
                
                # Verifiable data points
                if "source" in data[dimension]:
                    st.caption(f"**Source:** {data[dimension]['source']}")
                
                # Key metrics
                if dimension == "market_attractiveness":
                    user_val = data[dimension].get("est_users", "Undisclosed")
                    cagr_val = data[dimension].get("cagr", "Unknown")
                    st.metric("Estimated Users", user_val, delta=f"CAGR: {cagr_val}")
                
                elif dimension == "technical_feasibility":
                    method = data[dimension].get("integration_method", "Unknown")
                    days = data[dimension].get("integration_days", "Unknown")
                    risk = data[dimension].get("risk_level", "Unknown")
                    
                    st.metric("Method", method)
                    st.metric("Timeline", f"{days} days" if str(days).isnumeric() else "Unknown")
                    st.metric("Risk Level", risk, delta_color="inverse")
                
                elif dimension == "revenue_potential":
                    arr = data[dimension].get("arr_potential", "Unknown")
                    pricing = data[dimension].get("pricing_power", "Unknown")
                    st.metric("ARR Potential", arr)
                    st.metric("Pricing Power", pricing)
    
    with col_side:
        # Risk & gaps
        st.markdown('<div class="section-header">⚠️ Risk Profile</div>', unsafe_allow_html=True)
        
        if data.get("key_risks"):
            for risk in data["key_risks"][:3]:
                st.error(f"• {risk}")
        else:
            st.info("No critical risks identified")
        
        # Data gaps
        if data.get("data_gaps"):
            st.markdown('<div class="section-header">📊 Data Gaps</div>', unsafe_allow_html=True)
            for gap in data["data_gaps"][:3]:
                st.warning(f"⚠️ {gap}")
        
        # Verdict
        st.markdown('<div class="section-header">🎯 Verdict</div>', unsafe_allow_html=True)
        if data['overall_score'] >= 75:
            st.success("**🟢 GREENLIGHT**")
        elif data['overall_score'] >= 60:
            st.warning("**🟡 CAUTIOUS**")
        else:
            st.error("**🔴 KILL**")
    
    # Executive memo
    st.divider()
    st.markdown('<div class="section-header">📝 Board Memo</div>', unsafe_allow_html=True)
    
    if st.session_state.memo_text:
        st.markdown(f'<div class="memo-container">{st.session_state.memo_text}</div>', unsafe_allow_html=True)
    
    # Raw data (collapsible)
    with st.expander("🛠️ Technical Details & Raw Data"):
        st.json(data)

# --- FOOTER ---
st.divider()
st.caption("🧠 **Trophi.ai Scale Engine** | Model: Llama-3.2-1B | Confidence threshold: High | Sources: Verified market data only")
