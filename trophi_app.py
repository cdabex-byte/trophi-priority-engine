import streamlit as st
import json
import re
from huggingface_hub import InferenceClient

# === JSON PARSER UTILITY (Critical Fix) ===
def parse_json_safely(text, phase_name="Parse"):
    """
    Aggressive JSON extraction with debugging
    Handles markdown, extra text, malformed JSON
    """
    try:
        # Step 1: Remove markdown code fences
        text = re.sub(r'```json|```', '', text)
        
        # Step 2: Find JSON object boundaries (first { to last })
        start = text.find('{')
        end = text.rfind('}')
        
        if start == -1 or end == -1:
            raise ValueError("No JSON object boundaries found")
        
        json_str = text[start:end+1].strip()
        
        # Step 3: Parse JSON
        return json.loads(json_str)
        
    except Exception as e:
        st.error(f"❌ **{phase_name} Failed**: {str(e)}")
        with st.expander(f"🐛 Debug: Raw {phase_name} Response"):
            st.code(text[:1000], language="text")
        st.stop()

# === ENTERPRISE MODEL (Unchanged) ===
TROPHI_OPERATING_MODEL = {
    "current_state": {
        "team": {"total": 22, "engineering": 8, "burn_rate": "$85K/month", "runway": "38 months"},
        "capacity": {"available_hours_per_sprint": 320},
        "metrics": {"ltv": "$205", "cac": "$52", "mrr": "$47K"}
    },
    "integration_benchmarks": {
        "direct_api": {"hours": 40, "cost": "$4,800", "timeline": "5 days"},
        "udp_telemetry": {"hours": 120, "cost": "$14,400", "timeline": "14 days"}
    }
}

# === RUBRIC (Unchanged) ===
investor_granular_rubric = """[FORCED QUANTIFICATION RULES...]"""

# === UI STYLING (Unchanged) ===
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');
    body { font-family: 'Inter', sans-serif; background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #e2e8f0; }
    .investor-header { background: rgba(15, 23, 42, 0.8); backdrop-filter: blur(20px); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 20px; padding: 40px; margin-bottom: 30px; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); }
    .metric-card { background: linear-gradient(135deg, rgba(99, 102, 241, 0.9) 0%, rgba(124, 58, 237, 0.9) 100%); border-radius: 16px; padding: 25px; border: 1px solid rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3); }
    .metric-value { font-weight: 900; font-size: 3rem; color: white; }
    .metric-label { color: rgba(255, 255, 255, 0.8); font-weight: 600; font-size: 0.85rem; text-transform: uppercase; }
    .dev-impact-card { background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(99, 102, 241, 0.3); border-radius: 12px; padding: 20px; margin: 10px 0; }
    .fin-model-section { background: rgba(15, 23, 42, 0.5); border-left: 4px solid #6366f1; padding: 15px 20px; margin: 10px 0; border-radius: 0 8px 8px 0; }
    .bull-case { border-left-color: #10b981; }
    .bear-case { border-left-color: #ef4444; }
    </style>
""", unsafe_allow_html=True)

# === SIDEBAR ===
with st.sidebar:
    st.image("https://img.logoipsum.com/297.svg", width=150)
    st.markdown("### 🎯 Evaluation Controls")
    sprint_capacity = st.slider("Available Sprint Hours", 200, 600, 320)
    min_arr = st.number_input("Min ARR Threshold ($K)", 100, 1000, 250) * 1000
    max_cac = st.number_input("Max CAC ($)", 50, 150, 65)
    
    st.divider()
    st.caption("📊 **Current State**")
    st.metric("Runway", "38 months", "$3.23M total")
    st.metric("Burn Rate", "$85K/month", "1.8% weekly")
    st.metric("MRR", "$47K", "+$8K M/M")

# === SESSION STATE ===
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "ai_data" not in st.session_state:
    st.session_state.ai_data = None
if "memo_text" not in st.session_state:
    st.session_state.memo_text = None

# === INPUT ===
st.markdown('<div class="investor-header">', unsafe_allow_html=True)
st.title("🧠 Trophi.ai Scale Decision Engine")
st.caption("**Investor-Grade Opportunity Assessment** | A16Z SPEEDRUN Portfolio")
st.markdown('</div>', unsafe_allow_html=True)

col_input, col_btn = st.columns([4, 1])
with col_input:
    target_name = st.text_input("", 
                                placeholder="Enter opportunity: 'iRacing F1 25 API', 'Logitech G Pro Partnership'...")
with col_btn:
    analyze_btn = st.button("⚡ Execute Analysis", use_container_width=True, type="primary")

# === 6-PHASE PIPELINE ===
if analyze_btn and target_name:
    if "HF_API_TOKEN" not in st.secrets:
        st.error("❌ Missing 'HF_API_TOKEN' in Streamlit Secrets")
        st.stop()
    
    client = InferenceClient(token=st.secrets["HF_API_TOKEN"])
    
    with st.status("Executing 6-phase strategic analysis pipeline...", expanded=True):
        # === PHASE 1: MARKET INTELLIGENCE ===
        st.write("📡 **Phase 1**: Gathering verifiable market data...")
        market_prompt = f"""<|start_header_id|>system<|end_header_id|>
You are a market intelligence analyst at A16Z. Extract ONLY verifiable numbers with URLs.

**MANDATORY SOURCES:**
- SteamSpy: https://steamspy.com/app/[ID]
- Newzoo: https://newzoo.com/insights/...
- Company IR: https://investor.logitech.com/...

**IF UNAVAILABLE:** Use "Undisclosed (est. 10K-50K based on [similar_title])"

Return PURE JSON:
{{"tam": "$50M", "sam": "$20M", "som": "$1.5M", "active_users": "15,000", "source": "SteamSpy: https://steamspy.com/app/12345", "cagr": "7.3%", "confidence": 85}}<|eot_id|>
<|start_header_id|>user<|end_header_id|>
Target: {target_name}
Provide market sizing with source URLs.<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
        
        try:
            market = client.chat_completion(model="meta-llama/Llama-3.2-1B-Instruct", messages=[{"role": "user", "content": market_prompt}], max_tokens=400, temperature=0.1)
            market_data = parse_json_safely(market.choices[0].message.content, "Phase 1 Market")
        except Exception as e:
            st.error(f"Phase 1 failed: {e}")
            st.stop()
        
        # === PHASE 2: TECHNICAL ARCHITECTURE ===
        st.write("⚙️ **Phase 2**: Mapping integration architecture...")
        tech_prompt = f"""<|start_header_id|>system<|end_header_id|>
You are a principal engineer. Specify exact integration spec.

**API EXAMPLE:**
{{"method": "API", "endpoint": "https://api.iracing.com/v1/telemetry", "hours": 40, "cost_at_120_hr": "$4,800", "timeline_days": 5, "qa_days": 2, "team_pct_of_sprint": 12.5, "parallelizable": true}}

**UDP EXAMPLE:**
{{"method": "UDP", "endpoint": "Port 20777, 60Hz packets", "hours": 120, "cost_at_120_hr": "$14,400", "timeline_days": 14, "qa_days": 5, "team_pct_of_sprint": 37.5, "parallelizable": false}}

Return PURE JSON for {target_name}.<|eot_id|><|start_header_id|>user<|end_header_id|>
Target: {target_name}
Provide technical spec.<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
        
        tech = client.chat_completion(model="meta-llama/Llama-3.2-1B-Instruct", messages=[{"role": "user", "content": tech_prompt}], max_tokens=450, temperature=0.1)
        tech_data = parse_json_safely(tech.choices[0].message.content, "Phase 2 Tech")
        
        # === PHASE 3: FINANCIAL MODEL ===
        st.write("💰 **Phase 3**: Building 3-case P&L...")
        fin_prompt = f"""<|start_header_id|>system<|end_header_id|>
Build 3-case financial model with explicit assumptions.

**BASE CASE:**
{{"conversion": 1.5, "arr": "$420K", "payback": "94 days", "npv": "$1.2M", "assumptions": "Conservative 1.5% conversion, $19.99 pricing"}}

**BULL CASE:**
{{"conversion": 2.5, "arr": "$700K", "payback": "63 days", "npv": "$2.1M", "assumptions": "Partnership acceleration, $29.99 premium"}}

**BEAR CASE:**
{{"conversion": 0.8, "arr": "$224K", "payback": "157 days", "npv": "$0.4M", "assumptions": "50% integration delay, $9.99 churn risk"}}

Return PURE JSON with all 3 cases for {market_data['active_users']} users.<|eot_id|><|start_header_id|>user<|end_header_id|>
Users: {market_data['active_users']}
Build model.<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
        
        fin = client.chat_completion(model="meta-llama/Llama-3.2-1B-Instruct", messages=[{"role": "user", "content": fin_prompt}], max_tokens=600, temperature=0.1)
        fin_data = parse_json_safely(fin.choices[0].message.content, "Phase 3 Financial")
        
        # === PHASE 4: STRATEGIC POSITIONING ===
        st.write("🎯 **Phase 4**: Assessing strategic fit...")
        strategy_prompt = f"""<|start_header_id|>system<|end_header_id|>
Assess strategic fit and velocity.

**HIGH FIT (9-10):** iRacing, F1 series, Assetto Corsa
**MEDIUM FIT (6-8):** Logitech, Fanatec, Thrustmaster
**LOW FIT (3-5):** Valorant, Apex (requires CV)

**VELOCITY SCORING:**
- API access: +3 pts
- Partner commitment: +2 pts
- A16Z intro: +2 pts
- Existing relationship: +1 pt

Return PURE JSON:
{{"fit_score": 9, "alignment": "Core Racing", "moat_benefit": "15,000 coaching hours added", "competitors": ["VRS at $9.99", "Coach Dave at $19.99"], "velocity": 9, "speedrun_leverage": "A16Z intro to Fanatec CEO"}}<|eot_id|><|start_header_id|>user<|end_header_id|>
Target: {target_name}
Assess strategic fit.<|eot_id_id|><|start_header_id|>assistant<|end_header_id|>"""
        
        strategy = client.chat_completion(model="meta-llama/Llama-3.2-1B-Instruct", messages=[{"role": "user", "content": strategy_prompt}], max_tokens=450, temperature=0.1)
        strategy_data = parse_json_safely(strategy.choices[0].message.content, "Phase 4 Strategy")
        
        # === PHASE 5: CONSOLIDATE ===
        st.write("📊 **Phase 5**: Calculating final score...")
        
        # Calculate weighted score
        market_score = min(10, int(market_data['active_users'].replace(',', '')) / 10000) * 3.5
        tech_score = (10 - min(tech_data['hours'] / 48, 10)) * 2.5
        revenue_score = fin_data['base']['conversion'] * 10 / 1.5 * 2.5  # Normalize
        strategy_score = strategy_data['fit_score'] * 1.5
        
        ai_data = {
            "target": target_name,
            "overall_score": round(market_score + tech_score + revenue_score + strategy_score, 1),
            "confidence": market_data['confidence'],
            "market_attractiveness": {
                "tam": market_data['tam'], "sam": market_data['sam'], "som": market_data['som'],
                "active_users": market_data['active_users'], "cagr": market_data['cagr'],
                "score": round(min(10, int(market_data['active_users'].replace(',', '')) / 10000), 1),
                "source": market_data['source']
            },
            "technical_feasibility": {
                "method": tech_data['method'], "endpoint": tech_data.get('endpoint', 'N/A'),
                "hours": tech_data['hours'], "cost": tech_data['cost_at_120_hr'],
                "timeline_days": tech_data['timeline_days'], "qa_days": tech_data['qa_days'],
                "team_pct": round(tech_data['team_pct_of_sprint'], 1),
                "parallelizable": tech_data['parallelizable'],
                "score": round(10 - min(tech_data['hours'] / 48, 10), 1)
            },
            "revenue_potential": {
                "conversion_rate": fin_data['base']['conversion'],
                "arr": fin_data['base']['arr'],
                "payback_days": int(fin_data['base']['payback'].split()[0]),
                "score": round(fin_data['base']['conversion'] * 10 / 1.5, 1)
            },
            "strategic_fit": {
                "score": strategy_data['fit_score'],
                "alignment": strategy_data['alignment'],
                "moat_benefit": strategy_data['moat_benefit'],
                "competitors": strategy_data['competitors'],
                "velocity": strategy_data['velocity']
            },
            "dev_impact": {
                "hours_required": tech_data['hours'],
                "sprint_capacity_pct": round(tech_data['team_pct_of_sprint'], 1),
                "cost_at_120_hr": tech_data['cost_at_120_hr'],
                "parallelizable": tech_data['parallelizable'],
                "runway_impact": f"{int(tech_data['cost_at_120_hr'].split('$')[1].replace('K','000')) / 85000:.1%}"
            },
            "financial_model": fin_data
        }
        
        st.session_state.ai_data = ai_data
        st.session_state.analysis_done = True

# === DISPLAY RESULTS ===
if st.session_state.analysis_done and st.session_state.ai_data:
    # ... (display logic remains unchanged) ...

# === FOOTER ===
st.divider()
st.caption("📊 **Trophi.ai Scale Engine** | A16Z SPEEDRUN | Built with Hugging Face Inference API")
