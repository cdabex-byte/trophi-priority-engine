import streamlit as st
import json
import re
from huggingface_hub import InferenceClient

# === ENHANCED JSON PARSER with Retry Logic ===
def parse_json_safely(text, phase_name="Parse", fallback_data=None):
    """
    Ultra-robust JSON extraction with debug and fallback
    """
    try:
        # Debug: Show raw response first
        st.write(f"🔍 **Debug ({phase_name})**: Raw response length: {len(text)} chars")
        
        # Step 1: Aggressive markdown removal
        text = re.sub(r'```json|```', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\[.*?\]', '', text)  # Remove markdown links
        text = re.sub(r'\*\*.*?\*\*', '', text)  # Remove bold
        
        # Step 2: Find JSON boundaries
        start = text.find('{')
        end = text.rfind('}')
        
        if start == -1 or end == -1:
            st.warning(f"⚠️ No JSON boundaries found in {phase_name}, attempting fallback...")
            st.code(text[:500], language="text")  # Show first 500 chars
            
            # Use fallback data if provided
            if fallback_data:
                st.info(f"✅ Using fallback data for {phase_name}")
                return fallback_data
            
            raise ValueError("No JSON boundaries found and no fallback available")
        
        json_str = text[start:end+1].strip()
        
        # Step 3: Validate JSON is complete
        if json_str.count('{') != json_str.count('}'):
            st.warning(f"⚠️ Mismatched braces in {phase_name}, attempting repair...")
            # Simple repair: add missing braces
            if json_str.count('{') > json_str.count('}'):
                json_str += '}' * (json_str.count('{') - json_str.count('}'))
        
        # Step 4: Parse JSON
        return json.loads(json_str)
        
    except Exception as e:
        st.error(f"❌ **{phase_name} Failed**: {str(e)}")
        
        # Show debug info
        with st.expander(f"🐛 Debug: Full {phase_name} Response"):
            st.code(text, language="text")
        
        # Use fallback if available
        if fallback_data:
            st.info(f"⚠️ Using fallback data for {phase_name}")
            return fallback_data
        
        # Last resort: Return empty but valid structure
        st.warning(f"⚠️ Using empty fallback for {phase_name}")
        return {
            "tam": "$10M", "sam": "$5M", "som": "$0.5M", 
            "active_users": "Undisclosed (est. 10K)", "source": "Manual research required",
            "cagr": "5.0%", "confidence": 40, "fit_score": 5, "alignment": "Unknown",
            "moat_benefit": "Limited data", "competitors": ["Research needed"],
            "velocity": 5, "speedrun_leverage": "None identified",
            "conversion": 1.0, "arr": "$150K", "payback": "120 days", "npv": "$0.3M"
        }

# === ENTERPRISE MODEL ===
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

# === FALLBACK DATA (When API fails) ===
FALLBACK_MARKET = {
    "tam": "$50M", "sam": "$20M", "som": "$1.5M",
    "active_users": "Undisclosed (est. 10K-50K)",
    "source": "Industry estimation (manual research required)",
    "cagr": "5-10%", "confidence": 45
}

FALLBACK_TECH = {
    "method": "UDP", "endpoint": "Standard telemetry port",
    "hours": 120, "cost_at_120_hr": "$14,400",
    "timeline_days": 14, "team_pct_of_sprint": 37.5,
    "parallelizable": False
}

FALLBACK_FINANCIAL = {
    "base": {"conversion": 1.0, "arr": "$150K", "payback": "120 days", "npv": "$0.3M"},
    "bull": {"conversion": 2.0, "arr": "$300K", "payback": "80 days", "npv": "$0.6M"},
    "bear": {"conversion": 0.5, "arr": "$75K", "payback": "180 days", "npv": "$0.1M"}
}

# === UI STYLING ===
st.markdown("""
    <style>
    body { font-family: 'Inter', sans-serif; background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #e2e8f0; }
    .investor-header { background: rgba(15, 23, 42, 0.8); backdrop-filter: blur(20px); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 20px; padding: 40px; margin-bottom: 30px; }
    .metric-card { background: linear-gradient(135deg, rgba(99, 102, 241, 0.9) 0%, rgba(124, 58, 237, 0.9) 100%); border-radius: 16px; padding: 25px; border: 1px solid rgba(255, 255, 255, 0.1); }
    .metric-value { font-weight: 900; font-size: 3rem; color: white; }
    .metric-label { color: rgba(255, 255, 255, 0.8); font-weight: 600; font-size: 0.85rem; text-transform: uppercase; }
    .dev-impact-card { background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(99, 102, 241, 0.3); border-radius: 12px; padding: 20px; }
    .fin-model-section { background: rgba(15, 23, 42, 0.5); border-left: 4px solid #6366f1; padding: 15px 20px; margin: 10px 0; }
    .bull-case { border-left-color: #10b981; }
    .bear-case { border-left-color: #ef4444; }
    .fallback-banner { background: rgba(245, 158, 11, 0.2); border: 1px solid #f59e0b; border-radius: 8px; padding: 10px; margin: 10px 0; }
    </style>
""", unsafe_allow_html=True)

# === SIDEBAR ===
with st.sidebar:
    st.image("https://img.logoipsum.com/297.svg", width=150)
    st.markdown("### 🎯 Evaluation Controls")
    sprint_capacity = st.slider("Available Sprint Hours", 200, 600, 320, help="Engineering capacity per 2-week sprint")
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
if "used_fallback" not in st.session_state:
    st.session_state.used_fallback = False

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

# === ANALYSIS PIPELINE (With Fallbacks) ===
if analyze_btn and target_name:
    if "HF_API_TOKEN" not in st.secrets:
        st.error("❌ Missing 'HF_API_TOKEN' in Streamlit Secrets")
        st.stop()
    
    client = InferenceClient(token=st.secrets["HF_API_TOKEN"])
    st.session_state.used_fallback = False  # Reset fallback flag
    
    with st.status("Executing 6-phase strategic analysis pipeline...", expanded=True):
        
        # === PHASE 1: MARKET INTELLIGENCE (with fallback) ===
        st.write("📡 **Phase 1**: Gathering verifiable market data...")
        market_prompt = f"""<|start_header_id|>system<|end_header_id|>
You are a market intelligence analyst. Return ONLY a JSON object - no explanations, no markdown.

EXAMPLE OUTPUT:
{{"tam": "$50M", "sam": "$20M", "som": "$1.5M", "active_users": "15,000", "source": "SteamSpy", "cagr": "7.3%", "confidence": 85}}

TARGET: {target_name}

If data is unavailable, use "Undisclosed (est. 10K-50K)" and set confidence to 40.<|eot_id|><|start_header_id|>user<|end_header_id|>
Return JSON only.<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
        
        try:
            market = client.chat_completion(model="meta-llama/Llama-3.2-1B-Instruct", messages=[{"role": "user", "content": market_prompt}], max_tokens=400, temperature=0.1)
            market_data = parse_json_safely(market.choices[0].message.content, "Phase 1 Market", FALLBACK_MARKET)
            
            # Check if fallback was used
            if "fallback" in market_data.get('source', '').lower() or market_data['confidence'] < 50:
                st.session_state.used_fallback = True
                st.markdown('<div class="fallback-banner">⚠️ **Phase 1 Used Fallback Data** - Manual verification recommended</div>', unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"Phase 1 failed: {e}")
            market_data = FALLBACK_MARKET
            st.session_state.used_fallback = True
        
        # === PHASE 2: TECHNICAL ARCHITECTURE ===
        st.write("⚙️ **Phase 2**: Mapping integration architecture...")
        tech_prompt = f"""<|start_header_id|>system<|end_header_id|>
You are a principal engineer. Return ONLY a JSON object.

EXAMPLE OUTPUT:
{{"method": "API", "endpoint": "https://api.example.com/v1", "hours": 40, "cost_at_120_hr": "$4,800", "timeline_days": 5, "team_pct_of_sprint": 12.5, "parallelizable": true}}

TARGET: {target_name}<|eot_id|><|start_header_id|>user<|end_header_id|>
Return JSON only.<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
        
        try:
            tech = client.chat_completion(model="meta-llama/Llama-3.2-1B-Instruct", messages=[{"role": "user", "content": tech_prompt}], max_tokens=450, temperature=0.1)
            tech_data = parse_json_safely(tech.choices[0].message.content, "Phase 2 Tech", FALLBACK_TECH)
        except Exception as e:
            st.error(f"Phase 2 failed: {e}")
            tech_data = FALLBACK_TECH
        
        # === PHASE 3: FINANCIAL MODEL ===
        st.write("💰 **Phase 3**: Building 3-case P&L...")
        fin_prompt = f"""<|start_header_id|>system<|end_header_id|>
Build 3-case financial model. Return ONLY a JSON object.

EXAMPLE OUTPUT:
{{"base": {{"conversion": 1.5, "arr": "$420K", "payback": "94 days", "npv": "$1.2M"}}, "bull": {{"conversion": 2.5, "arr": "$700K", "payback": "63 days", "npv": "$2.1M"}}, "bear": {{"conversion": 0.8, "arr": "$224K", "payback": "157 days", "npv": "$0.4M"}}}}

USERS: {market_data['active_users']}<|eot_id|><|start_header_id|>user<|end_header_id|>
Return JSON only.<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
        
        try:
            fin = client.chat_completion(model="meta-llama/Llama-3.2-1B-Instruct", messages=[{"role": "user", "content": fin_prompt}], max_tokens=600, temperature=0.1)
            fin_data = parse_json_safely(fin.choices[0].message.content, "Phase 3 Financial", FALLBACK_FINANCIAL)
        except Exception as e:
            st.error(f"Phase 3 failed: {e}")
            fin_data = FALLBACK_FINANCIAL
        
        # === PHASE 4: STRATEGIC POSITIONING ===
        st.write("🎯 **Phase 4**: Assessing strategic fit...")
        strategy_prompt = f"""<|start_header_id|>system<|end_header_id|>
Assess strategic fit. Return ONLY a JSON object.

EXAMPLE OUTPUT:
{{"fit_score": 9, "alignment": "Core Racing", "moat_benefit": "15,000 hours data", "competitors": ["VRS at $9.99"], "velocity": 9, "speedrun_leverage": "A16Z intro to Fanatec"}}<|eot_id|><|start_header_id|>user<|end_header_id|>
Target: {target_name}
Return JSON only.<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
        
        try:
            strategy = client.chat_completion(model="meta-llama/Llama-3.2-1B-Instruct", messages=[{"role": "user", "content": strategy_prompt}], max_tokens=450, temperature=0.1)
            strategy_data = parse_json_safely(strategy.choices[0].message.content, "Phase 4 Strategy")
        except Exception as e:
            st.error(f"Phase 4 failed: {e}")
            strategy_data = {"fit_score": 5, "alignment": "Unknown", "moat_benefit": "Limited", "competitors": ["Research needed"], "velocity": 5, "speedrun_leverage": "None"}
        
        # Phase 5: Consolidate
        st.write("📊 **Phase 5**: Calculating final weighted score...")
        
        # Calculate weighted score
        try:
            users = int(market_data['active_users'].replace(',', '').split()[0]) if market_data['active_users'] != "Undisclosed (est. 10K-50K)" else 25000
        except:
            users = 25000
        
        market_score = min(10, users / 10000) * 3.5
        tech_score = (10 - min(tech_data['hours'] / 48, 10)) * 2.5
        revenue_score = fin_data['base']['conversion'] * 10 / 1.5 * 2.5
        strategy_score = strategy_data['fit_score'] * 1.5
        
        ai_data = {
            "target": target_name,
            "overall_score": round(market_score + tech_score + revenue_score + strategy_score, 1),
            "confidence": market_data['confidence'],
            "market_attractiveness": {
                "tam": market_data['tam'], "sam": market_data['sam'], "som": market_data['som'],
                "active_users": market_data['active_users'], "cagr": market_data['cagr'],
                "score": round(min(10, users / 10000), 1), "source": market_data['source']
            },
            "technical_feasibility": {
                "method": tech_data['method'], "endpoint": tech_data.get('endpoint', 'N/A'),
                "hours": tech_data['hours'], "cost": tech_data['cost_at_120_hr'],
                "timeline_days": tech_data['timeline_days'], "team_pct": round(tech_data['team_pct_of_sprint'], 1),
                "parallelizable": tech_data['parallelizable'], "score": round(10 - min(tech_data['hours'] / 48, 10), 1)
            },
            "revenue_potential": {
                "conversion_rate": fin_data['base']['conversion'], "arr": fin_data['base']['arr'],
                "payback_days": int(fin_data['base']['payback'].split()[0]), "npv": fin_data['base']['npv'],
                "score": round(fin_data['base']['conversion'] * 10 / 1.5, 1)
            },
            "strategic_fit": {
                "score": strategy_data['fit_score'], "alignment": strategy_data['alignment'],
                "moat_benefit": strategy_data['moat_benefit'], "competitors": strategy_data['competitors'],
                "velocity": strategy_data['velocity'], "speedrun_leverage": strategy_data['speedrun_leverage']
            },
            "dev_impact": {
                "hours_required": tech_data['hours'],
                "sprint_capacity_pct": round(tech_data['team_pct_of_sprint'], 1),
                "cost_at_120_hr": tech_data['cost_at_120_hr'],
                "parallelizable": tech_data['parallelizable'],
                "runway_impact": f"{int(tech_data['cost_at_120_hr'].split('$')[1].replace('K','000')) / 85000:.1%}"
            },
            "financial_model": fin_data,
            "used_fallback": st.session_state.used_fallback
        }
        
        st.session_state.ai_data = ai_data
        st.session_state.analysis_done = True

# === DISPLAY RESULTS (PROPERLY INDENTED) ===
if st.session_state.analysis_done and st.session_state.ai_data:
    data = st.session_state.ai_data
    
    # Show fallback warning if used
    if data.get('used_fallback', False):
        st.markdown('<div class="fallback-banner">⚠️ **This analysis used fallback estimates** - Please verify critical data manually</div>', unsafe_allow_html=True)
    
    # Header with score
    st.markdown(f"""
        <div class="investor-header">
            <h2>📊 Overall Score: {data['overall_score']}/100</h2>
            <p style="color: {'#10b981' if data['confidence'] >= 80 else '#f59e0b' if data['confidence'] >= 60 else '#ef4444'}; font-weight: 600;">
                Data Confidence: {data['confidence']}%
            </p>
            <p style="font-size: 1.1rem;"><strong>{data['target']}</strong></p>
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
    
    # === TABS (PROPERLY INDENTED) ===
    tab_market, tab_tech, tab_fin, tab_dev, tab_strat, tab_memo = st.tabs([
        "🌍 Market Evidence", "⚙️ Tech Specs", "💰 P&L Model", "👥 Dev Impact", "🎯 Strategy", "📝 Board Memo"
    ])
    
    with tab_market:
        st.subheader("Market Sizing & Evidence")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("TAM", data['market_attractiveness']['tam'])
            st.metric("SAM", data['market_attractiveness']['sam'])
            st.metric("SOM", data['market_attractiveness']['som'])
        with col2:
            st.metric("Active Users", data['market_attractiveness']['active_users'])
            st.metric("CAGR", data['market_attractiveness']['cagr'])
            st.metric("Market Score", f"{data['market_attractiveness']['score']}/10")
        
        st.success(f"**Source:** {data['market_attractiveness']['source']}")
        
        if data['confidence'] < 70:
            st.warning(f"⚠️ **Low Confidence**: {data['confidence']}% - Manual verification needed")
            st.caption("**Action:** Research user numbers from company IR or SteamSpy")
    
    with tab_tech:
        st.subheader("Integration Architecture")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Method", data['technical_feasibility']['method'])
            st.metric("Endpoint", data['technical_feasibility'].get('endpoint', 'N/A'))
            st.metric("Dev Hours", f"{data['technical_feasibility']['hours']}h")
        with col2:
            st.metric("Timeline", f"{data['technical_feasibility']['timeline_days']} days")
            st.metric("Risk Level", data['technical_feasibility'].get('risk_level', 'Medium'))
            st.metric("Tech Score", f"{data['technical_feasibility']['score']}/10")
        
        st.divider()
        st.subheader("Engineering Resource Requirements")
        st.metric("**Fully-Loaded Cost**", data['technical_feasibility']['cost'])
        st.metric("**% of Sprint Capacity**", f"{data['technical_feasibility']['team_pct']}%")
        
        if not data['dev_impact']['parallelizable']:
            st.error(f"❌ **Pipeline Block**: Blocks team for {data['technical_feasibility']['timeline_days']} days")
            st.warning(f"**Cost to De-Risk**: ${data['technical_feasibility']['hours']*150/1000:.1f}K contractor")
        else:
            st.success(f"✅ **Pipeline Efficient**: Can run with 1 other integration")
    
    with tab_fin:
        st.subheader("Financial Model (3-Case Analysis)")
        
        for case_name, case_data in [("📊 Base Case", 'base'), ("🐂 Bull Case", 'bull'), ("🐻 Bear Case", 'bear')]:
            st.markdown(f'<div class="fin-model-section {"bull-case" if case_name == "🐂 Bull Case" else "bear-case" if case_name == "🐻 Bear Case" else ""}">', unsafe_allow_html=True)
            st.subheader(case_name)
            col1, col2, col3 = st.columns(3)
            col1.metric("Conversion", f"{data['financial_model'][case_data]['conversion']}%")
            col2.metric("ARR", data['financial_model'][case_data]['arr'])
            col3.metric("Payback", data['financial_model'][case_data]['payback'])
            st.markdown('</div>', unsafe_allow_html=True)
        
        if int(data['financial_model']['base']['payback'].split()[0]) > 90:
            st.error("❌ **Payback exceeds 90-day target**")
        else:
            st.success("✅ **Payback meets target**")
    
    with tab_dev:
        st.subheader("Engineering Capacity Impact")
        st.metric("Sprint Capacity Used", f"{data['dev_impact']['sprint_capacity_pct']}%")
        st.progress(data['dev_impact']['sprint_capacity_pct']/100)
        st.metric("Runway Impact", data['dev_impact']['runway_impact'])
        
        if float(data['dev_impact']['runway_impact'].replace('%', '')) > 10:
            st.warning("⚠️ **High burn impact** - Consider contractor or deferral")
    
    with tab_strat:
        st.subheader("Strategic Positioning")
        st.metric("Fit Score", f"{data['strategic_fit']['score']}/10")
        st.metric("Velocity", f"{data['strategic_fit']['velocity']}/10")
        st.metric("Moat Benefit", data['strategic_fit']['moat_benefit'])
        
        st.subheader("Competitors")
        for comp in data['strategic_fit']['competitors']:
            st.caption(f"• {comp}")
        
        st.subheader("A16Z SPEEDRUN Leverage")
        st.success(f"🚀 {data['strategic_fit']['speedrun_leverage']}")
    
    with tab_memo:
        st.subheader("Board Investment Memo")
        memo_prompt = f"""<|start_header_id|>system<|end_header_id|>
Write a 500-word board memo. Verdict: {'GREENLIGHT' if data['overall_score'] >= 75 else 'CAUTIOUS' if data['overall_score'] >= 60 else 'KILL'}.

Include:
- Market: {data['market_attractiveness']['tam']}
- Tech: {data['technical_feasibility']['hours']}h
- Revenue: {data['financial_model']['base']['arr']}
- 30-day action plan<|eot_id|><|start_header_id|>user<|end_header_id|>
Create memo.<|eot_id_id|><|start_header_id|>assistant<|end_header_id|>"""
        
        if not st.session_state.memo_text:
            memo = client.chat_completion(model="meta-llama/Llama-3.2-1B-Instruct", messages=[{"role": "user", "content": memo_prompt}], max_tokens=1000, temperature=0.3)
            st.session_state.memo_text = memo.choices[0].message.content
        
        st.markdown(st.session_state.memo_text)

# === FOOTER ===
st.divider()
st.caption("📊 **Trophi.ai Scale Engine** | A16Z SPEEDRUN | Data confidence threshold: High | Built with Hugging Face")
