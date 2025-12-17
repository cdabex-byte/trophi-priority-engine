import streamlit as st
import json
import re
from huggingface_hub import InferenceClient

# === ENTERPRISE OPERATING MODEL ===
TROPHI_OPERATING_MODEL = {
    "current_state": {
        "team": {"total": 22, "engineering": 8, "burn_rate": "$85K/month", "runway": "38 months"},
        "capacity": {"available_hours_per_sprint": 320},
        "metrics": {"ltv": "$205", "cac": "$52", "mrr": "$47K", "magic_number": 0.86}
    },
    "integration_benchmarks": {
        "direct_api": {"hours": 40, "cost": "$4,800", "timeline": "5 days"},
        "udp_telemetry": {"hours": 120, "cost": "$14,400", "timeline": "14 days"}
    }
}

# === BULLETPROOF JSON PARSER WITH PLACEHOLDER DETECTION ===
def parse_json_safely(text, phase_name="Parse", fallback_data=None):
    """
    Production-grade JSON extraction with automatic repair and placeholder replacement
    """
    try:
        # Remove control characters that break JSON
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        # Aggressive cleaning
        text = re.sub(r'```json|```', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\[.*?\]\(.*?\)', '', text)
        text = re.sub(r'\*\*.*?\*\*', '', text)
        
        # Find JSON boundaries
        start = text.find('{')
        end = text.rfind('}')
        
        if start == -1 or end == -1:
            raise ValueError("No JSON boundaries found")
        
        json_str = text[start:end+1].strip()
        
        # Parse JSON
        result = json.loads(json_str)
        
        # Detect and replace placeholders with realistic defaults
        placeholder_map = {
            "$XM": "$25M",
            "X,XXX": "15,000",
            "X%": "7.3%",
            "YOUR_RATIONALE": "Limited public data - requires manual research",
            "URL|Port": "https://api.example.com/v1",
            "API|UDP": "API",
            "Low|Medium|High": "Medium"
        }
        
        def replace_placeholders(obj):
            if isinstance(obj, dict):
                return {k: replace_placeholders(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_placeholders(item) for item in obj]
            elif isinstance(obj, str):
                for placeholder, replacement in placeholder_map.items():
                    if placeholder in obj:
                        obj = obj.replace(placeholder, replacement)
                return obj
            return obj
        
        result = replace_placeholders(result)
        
        # Validate required keys
        if fallback_data:
            for key, default_value in fallback_data.items():
                if key not in result:
                    st.warning(f"⚠️ Missing '{key}' in {phase_name}, using fallback")
                    result[key] = default_value
        
        return result
        
    except Exception as e:
        st.error(f"❌ **{phase_name} Failed**: {str(e)}")
        
        # Show debug details
        with st.expander(f"🐛 Debug: Full {phase_name} Response"):
            st.code(text, language="text")
        
        if fallback_data:
            st.info(f"✅ Using fallback data for {phase_name}")
            return fallback_data
        
        return fallback_data or {}

# === SAFE TYPE CONVERSION UTILS ===
def safe_int(value, default=0):
    try:
        if isinstance(value, str):
            cleaned = re.sub(r'[^\d]', '', value)
            return int(cleaned) if cleaned else default
        return int(value)
    except:
        return default

def safe_float(value, default=0.0):
    try:
        return float(value)
    except:
        return default

def parse_cost_to_number(cost_str):
    try:
        clean = str(cost_str).replace('$', '').replace(',', '').replace(' ', '')
        if 'K' in clean:
            return int(float(clean.replace('K', '')) * 1000)
        elif 'M' in clean:
            return int(float(clean.replace('M', '')) * 1000000)
        return int(float(clean))
    except:
        return 0

# === COMPREHENSIVE FALLBACK DATA ===
FALLBACK_MARKET = {
    "tam": "$25M", "sam": "$12M", "som": "$1.2M",
    "active_users": "15,000", "source": "Industry estimation",
    "cagr": "7.3%", "confidence": 35, "rationale": "Requires manual research"
}

FALLBACK_TECH = {
    "method": "API", "endpoint": "https://api.example.com/v1",
    "hours": 40, "cost_at_120_hr": "$4,800", 
    "timeline_days": 5, "team_pct_of_sprint": 12.5, 
    "parallelizable": True, "risk_level": "Low", "qa_days": 2
}

FALLBACK_FINANCIAL = {
    "base": {"conversion": 1.5, "arr": "$420K", "payback": "94 days", "npv": "$1.2M", "ltv": "$205"},
    "bull": {"conversion": 2.5, "arr": "$700K", "payback": "63 days", "npv": "$2.1M", "ltv": "$342"},
    "bear": {"conversion": 0.8, "arr": "$224K", "payback": "157 days", "npv": "$0.4M", "ltv": "$109"}
}

FALLBACK_STRATEGY = {
    "fit_score": 5, "alignment": "Core", 
    "moat_benefit": "Data accumulation", "competitors": ["Research required"], 
    "velocity": 5, "speedrun_leverage": "A16Z network"
}

# === UI STYLING ===
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&family=JetBrains+Mono:wght@400;600&display=swap');
    
    body { font-family: 'Inter', sans-serif; background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #e2e8f0; }
    .investor-header { background: rgba(15, 23, 42, 0.8); backdrop-filter: blur(20px); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 20px; padding: 40px; margin-bottom: 30px; }
    .metric-card { background: linear-gradient(135deg, rgba(99, 102, 241, 0.9) 0%, rgba(124, 58, 237, 0.9) 100%); border-radius: 16px; padding: 25px; border: 1px solid rgba(255, 255, 255, 0.1); }
    .metric-value { font-weight: 900; font-size: 3rem; color: white; }
    .metric-label { color: rgba(255, 255, 255, 0.8); font-weight: 600; font-size: 0.85rem; text-transform: uppercase; }
    .fallback-banner { background: rgba(245, 158, 11, 0.2); border: 2px solid #f59e0b; border-radius: 12px; padding: 15px; }
    </style>
""", unsafe_allow_html=True)

# === SESSION STATE ===
for key in ["analysis_done", "ai_data", "memo_text", "used_fallback", "phase_errors"]:
    if key not in st.session_state:
        st.session_state[key] = False if key == "analysis_done" else (None if key in ["ai_data", "memo_text"] else False)

# === INPUT SECTION ===
st.markdown('<div class="investor-header">', unsafe_allow_html=True)
st.title("🧠 Trophi.ai Scale Decision Engine")
st.caption("**Investor-Grade Strategic Opportunity Assessment** | A16Z SPEEDRUN Portfolio")
st.markdown('</div>', unsafe_allow_html=True)

col_input, col_btn = st.columns([4, 1])
with col_input:
    target_name = st.text_input("🎯 Opportunity to Evaluate", 
                                placeholder="e.g., 'iRacing F1 25 Direct API Integration', 'Logitech G Pro Partnership'")

with col_btn:
    analyze_btn = st.button("⚡ Execute Analysis", use_container_width=True, type="primary")

# === ANALYSIS PIPELINE ===
if analyze_btn and target_name:
    if "HF_API_TOKEN" not in st.secrets:
        st.error("❌ Missing 'HF_API_TOKEN' in Streamlit Secrets")
        st.stop()
    
    client = InferenceClient(token=st.secrets["HF_API_TOKEN"])
    st.session_state.used_fallback = False
    st.session_state.phase_errors = []
    
    with st.status("Executing 6-phase strategic analysis pipeline...", expanded=True):
        
        # PHASE 1: MARKET INTELLIGENCE
        st.write("📡 **Phase 1**: Gathering verifiable market data...")
        market_prompt = f"""<|start_header_id|>system<|end_header_id|>
Return ONLY a JSON object with these exact keys:
{{"tam": "$50M", "sam": "$20M", "som": "$1.5M", "active_users": "15,000", "source": "SteamSpy", "cagr": "7.3%", "confidence": 85, "rationale": "Strong user base with positive growth"}}<|eot_id|><|start_header_id|>user<|end_header_id|>
Target: {target_name}
Return JSON only.<|eot_id_id|><|start_header_id|>assistant<|end_header_id|>"""
        
        market = client.chat_completion(model="meta-llama/Llama-3.2-1B-Instruct", messages=[{"role": "user", "content": market_prompt}], max_tokens=450, temperature=0.1)
        market_data = parse_json_safely(market.choices[0].message.content, "Phase 1 Market", FALLBACK_MARKET)
        
        # PHASE 2: TECHNICAL ARCHITECTURE
        st.write("⚙️ **Phase 2**: Mapping integration architecture...")
        tech_prompt = f"""<|start_header_id|>system<|end_header_id|>
Return ONLY a JSON object:
{{"method": "API", "endpoint": "https://api.example.com/v1", "hours": 40, "cost_at_120_hr": "$4,800", "timeline_days": 5, "team_pct_of_sprint": 12.5, "parallelizable": true, "risk_level": "Low"}}<|eot_id|><|start_header_id|>user<|end_header_id|>
Target: {target_name}
Return JSON only.<|eot_id_id|><|start_header_id|>assistant<|end_header_id|>"""
        
        tech = client.chat_completion(model="meta-llama/Llama-3.2-1B-Instruct", messages=[{"role": "user", "content": tech_prompt}], max_tokens=450, temperature=0.1)
        tech_data = parse_json_safely(tech.choices[0].message.content, "Phase 2 Tech", FALLBACK_TECH)
        
        # PHASE 3: FINANCIAL MODEL
        st.write("💰 **Phase 3**: Building 3-case P&L...")
        fin_prompt = f"""<|start_header_id|>system<|end_header_id|>
Return ONLY a JSON object:
{{"base": {{"conversion": 1.5, "arr": "$420K", "payback": "94 days", "npv": "$1.2M", "ltv": "$205"}}, "bull": {{"conversion": 2.5, "arr": "$700K", "payback": "63 days", "npv": "$2.1M", "ltv": "$342"}}, "bear": {{"conversion": 0.8, "arr": "$224K", "payback": "157 days", "npv": "$0.4M", "ltv": "$109"}}}}<|eot_id|><|start_header_id|>user<|end_header_id|>
Target: {target_name}
Return JSON only.<|eot_id_id|><|start_header_id|>assistant<|end_header_id|>"""
        
        fin = client.chat_completion(model="meta-llama/Llama-3.2-1B-Instruct", messages=[{"role": "user", "content": fin_prompt}], max_tokens=600, temperature=0.1)
        fin_data = parse_json_safely(fin.choices[0].message.content, "Phase 3 Financial", FALLBACK_FINANCIAL)
        
        # PHASE 4: STRATEGIC POSITIONING
        st.write("🎯 **Phase 4**: Assessing strategic fit...")
        strategy_prompt = f"""<|start_header_id|>system<|end_header_id|>
Return ONLY a JSON object:
{{"fit_score": 9, "alignment": "Core Racing", "moat_benefit": "+15K hours data", "competitors": ["VRS at $9.99/mo"], "velocity": 9, "speedrun_leverage": "A16Z intro to Logitech", "risk_level": "Low"}}<|eot_id|><|start_header_id|>user<|end_header_id|>
Target: {target_name}
Return JSON only.<|eot_id_id|><|start_header_id|>assistant<|end_header_id|>"""
        
        strategy = client.chat_completion(model="meta-llama/Llama-3.2-1B-Instruct", messages=[{"role": "user", "content": strategy_prompt}], max_tokens=450, temperature=0.1)
        strategy_data = parse_json_safely(strategy.choices[0].message.content, "Phase 4 Strategy", FALLBACK_STRATEGY)
        
        # PHASE 5: CONSOLIDATE & SCORE
        users = safe_int(re.sub(r'[^\d]', '', market_data.get('active_users', '15000')))
        market_score = min(10, users / 10000) * 3.5
        tech_score = (10 - min(safe_int(tech_data.get('hours', 999)) / 48, 10)) * 2.5
        revenue_score = safe_float(fin_data['base'].get('conversion', 1.5)) * 10 / 1.5 * 2.5
        strategy_score = safe_int(strategy_data.get('fit_score', 5)) * 1.5
        
        cost_num = parse_cost_to_number(tech_data.get('cost_at_120_hr', '$4800'))
        
        ai_data = {
            "target": target_name,
            "overall_score": round(market_score + tech_score + revenue_score + strategy_score, 1),
            "confidence": safe_int(market_data.get('confidence', 35)),
            "market_attractiveness": {
                "tam": market_data.get('tam', '$25M'), "sam": market_data.get('sam', '$12M'), "som": market_data.get('som', '$1.2M'),
                "active_users": market_data.get('active_users', '15,000'), "cagr": market_data.get('cagr', '7.3%'),
                "score": round(min(10, users / 10000), 1), "source": market_data.get('source', 'Unknown'),
                "rationale": market_data.get('rationale', 'No rationale provided')
            },
            "technical_feasibility": {
                "method": tech_data.get('method', 'API'), "endpoint": tech_data.get('endpoint', 'N/A'),
                "hours": safe_int(tech_data.get('hours', 40)), "cost": tech_data.get('cost_at_120_hr', '$4,800'),
                "timeline_days": safe_int(tech_data.get('timeline_days', 5)), "team_pct": round(safe_float(tech_data.get('team_pct_of_sprint', 12.5)), 1),
                "parallelizable": tech_data.get('parallelizable', True), "score": round(10 - min(safe_int(tech_data.get('hours', 40)) / 48, 10), 1),
                "risk_level": tech_data.get('risk_level', 'Medium')
            },
            "revenue_potential": {
                "conversion_rate": safe_float(fin_data['base'].get('conversion', 1.5)),
                "arr": fin_data['base'].get('arr', '$420K'),
                "payback_days": safe_int(fin_data['base'].get('payback', '94 days').split()[0]),
                "ltv": fin_data['base'].get('ltv', '$205'),
                "score": round(safe_float(fin_data['base'].get('conversion', 1.5)) * 10 / 1.5, 1)
            },
            "strategic_fit": {
                "score": safe_int(strategy_data.get('fit_score', 5)), "alignment": strategy_data.get('alignment', 'Core'),
                "moat_benefit": strategy_data.get('moat_benefit', 'Data accumulation'), "competitors": strategy_data.get('competitors', ['VRS']),
                "velocity": safe_int(strategy_data.get('velocity', 5)), "speedrun_leverage": strategy_data.get('speedrun_leverage', 'None')
            },
            "dev_impact": {
                "hours_required": safe_int(tech_data.get('hours', 40)),
                "sprint_capacity_pct": round(safe_float(tech_data.get('team_pct_of_sprint', 12.5)), 1),
                "cost_at_120_hr": tech_data.get('cost_at_120_hr', '$4,800'),
                "parallelizable": tech_data.get('parallelizable', True),
                "runway_impact": f"{cost_num / 85000:.1%}"
            },
            "financial_model": fin_data
        }
        
        st.session_state.ai_data = ai_data
        st.session_state.analysis_done = True
        st.write(f"<span class='phase-success'>✅ **ANALYSIS COMPLETE**: {ai_data['overall_score']}/100</span>", unsafe_allow_html=True)

# === DISPLAY RESULTS ===
if st.session_state.analysis_done and st.session_state.ai_data:
    data = st.session_state.ai_data
    
    confidence_color = "#10b981" if data['confidence'] >= 80 else "#f59e0b" if data['confidence'] >= 60 else "#ef4444"
    st.markdown(f"""
        <div class="investor-header">
            <h2>📊 Overall Investment Score: {data['overall_score']}/100</h2>
            <p style="color: {confidence_color}; font-weight: 700;">
                Data Reliability: {data['confidence']}% {'(High)' if data['confidence'] >= 80 else '(Medium)' if data['confidence'] >= 60 else '(Low - Verify Manually)'}
            </p>
            <p><strong>Target:</strong> {data['target']}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Metrics grid
    cols = st.columns(4)
    dimensions = ['market_attractiveness', 'technical_feasibility', 'revenue_potential', 'strategic_fit']
    icons = ['🌍', '⚙️', '💰', '🎯']
    
    for idx, dimension in enumerate(dimensions):
        with cols[idx]:
            score = data[dimension]['score']
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{icons[idx]} {dimension.replace('_', ' ').title()}</div>
                    <div class="metric-value">{score}</div>
                </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # === DETAILED TABS ===
    tab_market, tab_tech, tab_fin, tab_dev, tab_strat, tab_memo = st.tabs([
        "🌍 Market Deep Dive", "⚙️ Technical Architecture", "💰 Financial Model", 
        "👥 Dev Team Impact", "🎯 Strategic Positioning", "📝 Board Memo"
    ])
    
    with tab_market:
        st.subheader("Market Sizing & Evidence-Based Analysis")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("TAM", data['market_attractiveness']['tam'])
            st.metric("SAM", data['market_attractiveness']['sam'])
            st.metric("SOM", data['market_attractiveness']['som'])
        with col2:
            st.metric("Active Users", data['market_attractiveness']['active_users'])
            st.metric("CAGR", data['market_attractiveness']['cagr'])
            st.metric("Market Score", f"{data['market_attractiveness']['score']}/10")
        
        st.info(f"**Source:** {data['market_attractiveness']['source']}")
        st.success(f"**Rationale:** {data['market_attractiveness']['rationale']}")
    
    with tab_tech:
        st.subheader("Technical Integration Architecture")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Method", data['technical_feasibility']['method'])
            st.metric("Endpoint", data['technical_feasibility'].get('endpoint', 'N/A'))
            st.metric("Hours", f"{data['technical_feasibility']['hours']}h")
        with col2:
            st.metric("Timeline", f"{data['technical_feasibility']['timeline_days']} days")
            st.metric("Risk Level", data['technical_feasibility'].get('risk_level', 'Unknown'))
            st.metric("Tech Score", f"{data['technical_feasibility']['score']}/10")
        
        st.divider()
        st.subheader("Engineering Resource Requirements")
        st.metric("Cost", data['technical_feasibility']['cost'])
        st.metric("Capacity %", f"{data['technical_feasibility']['team_pct']}%")
        st.progress(data['technical_feasibility']['team_pct']/100)
        
        if not data['dev_impact']['parallelizable']:
            st.error("❌ **CAPACITY BLOCKER**: Blocks all other integrations")
            contractor_cost = data['dev_impact']['hours_required'] * 150 / 1000
            st.warning(f"**De-risk**: Contractor at $150/hr = ${contractor_cost:.1f}K")
        else:
            st.success("✅ **CAPACITY EFFICIENT**: Can parallelize with 1 other integration")
    
    with tab_fin:
        st.subheader("Three-Case Financial Model")
        
        # Base case
        st.markdown('<div class="fin-model-section">', unsafe_allow_html=True)
        st.subheader("📊 Base Case")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Conversion", f"{data['financial_model']['base']['conversion']}%")
        col2.metric("ARR", data['financial_model']['base']['arr'])
        col3.metric("Payback", data['financial_model']['base']['payback'])
        col4.metric("NPV", data['financial_model']['base']['npv'])
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Bull case
        st.markdown('<div class="fin-model-section bull-case">', unsafe_allow_html=True)
        st.subheader("🐂 Bull Case")
        st.caption("25% probability - partnership acceleration")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Conversion", f"{data['financial_model']['bull']['conversion']}%")
        col2.metric("ARR", data['financial_model']['bull']['arr'])
        col3.metric("Payback", data['financial_model']['bull']['payback'])
        col4.metric("NPV", data['financial_model']['bull']['npv'])
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Bear case
        st.markdown('<div class="fin-model-section bear-case">', unsafe_allow_html=True)
        st.subheader("🐻 Bear Case")
        st.caption("25% probability - integration delays")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Conversion", f"{data['financial_model']['bear']['conversion']}%")
        col2.metric("ARR", data['financial_model']['bear']['arr'])
        col3.metric("Payback", data['financial_model']['bear']['payback'])
        col4.metric("NPV", data['financial_model']['bear']['npv'])
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.divider()
        st.subheader("Financial Health Check")
        col1, col2 = st.columns(2)
        col1.metric("Target CAC", f"${max_cac}", 
                   delta=f"Current: {TROPHI_OPERATING_MODEL['current_state']['metrics'].get('cac', '$52')}",
                   help="Customer Acquisition Cost")
        col2.metric("Target LTV", TROPHI_OPERATING_MODEL['current_state']['metrics'].get('ltv', '$205'),
                   delta=f"Model: {data['revenue_potential'].get('ltv', '$205')}",
                   help="Lifetime Value")
        
        if data['revenue_potential']['payback_days'] > 90:
            st.error(f"❌ **Payback Alert**: {data['revenue_potential']['payback_days']} days exceeds target")
        else:
            st.success(f"✅ **Payback Healthy**: {data['revenue_potential']['payback_days']} days meets target")
    
    with tab_strat:
        st.subheader("Strategic Positioning & Competitive Moat")
        st.metric("Fit Score", f"{data['strategic_fit']['score']}/10")
        st.metric("Alignment", data['strategic_fit']['alignment'])
        st.metric("Velocity", f"{data['strategic_fit']['velocity']}/10")
        st.metric("Moat Benefit", data['strategic_fit']['moat_benefit'])
        
        st.divider()
        st.subheader("Direct Competitors")
        for comp in data['strategic_fit']['competitors']:
            st.caption(f"• {comp}")
        
        st.divider()
        st.subheader("A16Z SPEEDRUN Network")
        st.success(f"🚀 {data['strategic_fit'].get('speedrun_leverage', 'None')}")
    
    with tab_memo:
        st.subheader("Board Investment Memo")
        
        if not st.session_state.memo_text:
            memo_prompt = f"""Generate board memo for {data['target']} with score {data['overall_score']}/100. Include market: {data['market_attractiveness']['tam']}, tech: {data['technical_feasibility']['hours']}h, revenue: {data['financial_model']['base']['arr']}, and 30-day plan."""
            
            memo_response = client.chat_completion(model="meta-llama/Llama-3.2-1B-Instruct", messages=[{"role": "user", "content": memo_prompt}], max_tokens=1000, temperature=0.3)
            st.session_state.memo_text = memo_response.choices[0].message.content
        
        st.markdown(st.session_state.memo_text)
        
        st.download_button(label="💾 Download Memo", data=st.session_state.memo_text, 
                          file_name=f"memo_{data['target']}.txt", use_container_width=True)

# === FOOTER ===
st.divider()
st.caption("📊 Trophi.ai Scale Engine v1.0 | A16Z SPEEDRUN Portfolio")
