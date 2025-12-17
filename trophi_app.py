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

# === ENTERPRISE OPERATING MODEL ===
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

# === MODERN UI STYLING ===
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');
    
    body {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #e2e8f0;
    }
    
    .investor-header {
        background: rgba(15, 23, 42, 0.8);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 20px;
        padding: 40px;
        margin-bottom: 30px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    }
    
    .metric-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.9) 0%, rgba(124, 58, 237, 0.9) 100%);
        border-radius: 16px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
    }
    
    .metric-value {
        font-weight: 900;
        font-size: 3rem;
        color: white;
        font-family: 'Inter', sans-serif;
    }
    
    .metric-label {
        color: rgba(255, 255, 255, 0.8);
        font-weight: 600;
        font-size: 0.85rem;
        text-transform: uppercase;
    }
    
    .dev-impact-card {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
    }
    
    .fin-model-section {
        background: rgba(15, 23, 42, 0.5);
        border-left: 4px solid #6366f1;
        padding: 15px 20px;
        margin: 10px 0;
        border-radius: 0 8px 8px 0;
    }
    
    .bull-case { border-left-color: #10b981; }
    .bear-case { border-left-color: #ef4444; }
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

# === INPUT SECTION ===
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

# === ANALYSIS PIPELINE ===
if analyze_btn and target_name:
    if "HF_API_TOKEN" not in st.secrets:
        st.error("❌ Missing 'HF_API_TOKEN' in Streamlit Secrets")
        st.stop()
    
    client = InferenceClient(token=st.secrets["HF_API_TOKEN"])
    
    with st.status("Executing 6-phase strategic analysis pipeline...", expanded=True):
        # Phase 1: Market Intelligence
        st.write("📡 **Phase 1**: Gathering verifiable market data...")
        market_prompt = f"""<|start_header_id|>system<|end_header_id|>
You are a market intelligence analyst. Extract ONLY verifiable numbers with sources.

Return PURE JSON:
{{"tam": "$50M", "sam": "$20M", "som": "$1.5M", "active_users": "15,000", "source": "SteamSpy", "cagr": "7.3%", "confidence": 85}}<|eot_id|><|start_header_id|>user<|end_header_id|>
Target: {target_name}
Provide market sizing.<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
        
        market = client.chat_completion(model="meta-llama/Llama-3.2-1B-Instruct", messages=[{"role": "user", "content": market_prompt}], max_tokens=400, temperature=0.1)
        market_data = parse_json_safely(market.choices[0].message.content, "Phase 1 Market")
        
        # Phase 2: Technical Architecture
        st.write("⚙️ **Phase 2**: Mapping integration architecture...")
        tech_prompt = f"""<|start_header_id|>system<|end_header_id|>
You are a principal engineer. Specify exact integration spec.

Return PURE JSON:
{{"method": "API", "endpoint": "https://api.example.com/v1", "hours": 40, "cost_at_120_hr": "$4,800", "timeline_days": 5, "team_pct_of_sprint": 12.5, "parallelizable": true}}<|eot_id|><|start_header_id|>user<|end_header_id|>
Target: {target_name}
Provide technical spec.<|eot_id_id|><|start_header_id|>assistant<|end_header_id|>"""
        
        tech = client.chat_completion(model="meta-llama/Llama-3.2-1B-Instruct", messages=[{"role": "user", "content": tech_prompt}], max_tokens=450, temperature=0.1)
        tech_data = parse_json_safely(tech.choices[0].message.content, "Phase 2 Tech")
        
        # Phase 3: Financial Model
        st.write("💰 **Phase 3**: Building 3-case P&L...")
        fin_prompt = f"""<|start_header_id|>system<|end_header_id|>
Build 3-case financial model.

Return PURE JSON:
{{"base": {{"conversion": 1.5, "arr": "$420K", "payback": "94 days", "npv": "$1.2M"}}, "bull": {{"conversion": 2.5, "arr": "$700K", "payback": "63 days", "npv": "$2.1M"}}, "bear": {{"conversion": 0.8, "arr": "$224K", "payback": "157 days", "npv": "$0.4M"}}}}<|eot_id|><|start_header_id|>user<|end_header_id|>
Users: {market_data['active_users']}
Build model.<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
        
        fin = client.chat_completion(model="meta-llama/Llama-3.2-1B-Instruct", messages=[{"role": "user", "content": fin_prompt}], max_tokens=600, temperature=0.1)
        fin_data = parse_json_safely(fin.choices[0].message.content, "Phase 3 Financial")
        
        # Phase 4: Strategic Positioning
        st.write("🎯 **Phase 4**: Assessing strategic fit...")
        strategy_prompt = f"""<|start_header_id|>system<|end_header_id|>
Assess strategic fit and velocity.

Return PURE JSON:
{{"fit_score": 9, "alignment": "Core Racing", "moat_benefit": "15,000 hours data", "competitors": ["VRS at $9.99"], "velocity": 9, "speedrun_leverage": "A16Z intro to Fanatec"}}<|eot_id|><|start_header_id|>user<|end_header_id|>
Target: {target_name}
Assess strategic fit.<|eot_id_id|><|start_header_id|>assistant<|end_header_id|>"""
        
        strategy = client.chat_completion(model="meta-llama/Llama-3.2-1B-Instruct", messages=[{"role": "user", "content": strategy_prompt}], max_tokens=450, temperature=0.1)
        strategy_data = parse_json_safely(strategy.choices[0].message.content, "Phase 4 Strategy")
        
        # Phase 5: Consolidate
        st.write("📊 **Phase 5**: Calculating weighted score...")
        
        # Calculate weighted score
        market_score = min(10, int(market_data['active_users'].replace(',', '')) / 10000) * 3.5
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
                "score": round(min(10, int(market_data['active_users'].replace(',', '')) / 10000), 1),
                "source": market_data['source']
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
            "financial_model": fin_data
        }
        
        st.session_state.ai_data = ai_data
        st.session_state.analysis_done = True

# === DISPLAY RESULTS (FIXED INDENTATION) ===
if st.session_state.analysis_done and st.session_state.ai_data:
    data = st.session_state.ai_data
    
    # Header with score and confidence
    st.markdown(f"""
        <div class="investor-header">
            <h2>📊 Overall Score: {data['overall_score']}/100</h2>
            <p style="color: { '#10b981' if data['confidence'] >= 80 else '#f59e0b' if data['confidence'] >= 60 else '#ef4444' }; font-weight: 600;">
                Data Confidence: {data['confidence']}%
            </p>
            <p style="font-size: 1.1rem;"><strong>{data['target']}</strong> | Llama-3.2-1B</p>
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
        
        st.success(f"**Data Source:** {data['market_attractiveness']['source']}")
        st.info(f"**Rationale:** {data['market_attractiveness']['rationale']}")
        
        if data['confidence'] < 70:
            st.warning(f"⚠️ **Verification Required**: Confidence is {data['confidence']}%")
            st.caption("Recommend: Manual research to confirm user numbers")
    
    with tab_tech:
        st.subheader("Integration Architecture")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Method", data['technical_feasibility']['method'])
            st.metric("Endpoint", data['technical_feasibility'].get('endpoint', 'N/A'))
            st.metric("Dev Hours", f"{data['technical_feasibility']['hours']}h")
        with col2:
            st.metric("Timeline", f"{data['technical_feasibility']['timeline_days']} days + {data['technical_feasibility'].get('qa_days', 2)} QA days")
            st.metric("Risk Level", data['technical_feasibility']['risk_level'])
            st.metric("Tech Score", f"{data['technical_feasibility']['score']}/10")
        
        st.divider()
        st.subheader("Engineering Resource Requirements")
        st.metric("**Fully-Loaded Cost**", data['technical_feasibility']['cost'])
        st.metric("**% of Sprint Capacity**", f"{data['technical_feasibility']['team_pct']}%")
        
        if not data['dev_impact']['parallelizable']:
            st.error(f"❌ **Pipeline Crisis**: Blocks team for {data['technical_feasibility']['timeline_days']} days")
            st.warning(f"**Mitigation**: Hire contractor at $150/hr = ${data['technical_feasibility']['hours']*150/1000:.1f}K extra")
        else:
            st.success(f"✅ **Pipeline Efficient**: Can run alongside 1 other integration")
    
    with tab_fin:
        st.subheader("Financial Model (3-Case Analysis)")
        
        # Base Case
        st.markdown('<div class="fin-model-section">', unsafe_allow_html=True)
        st.subheader("📊 Base Case (50% probability)")
        col1, col2, col3 = st.columns(3)
        col1.metric("Conversion Rate", f"{data['financial_model']['base']['conversion']}%")
        col2.metric("ARR Potential", data['financial_model']['base']['arr'])
        col3.metric("Payback Period", data['financial_model']['base']['payback'])
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Bull Case
        st.markdown('<div class="fin-model-section bull-case">', unsafe_allow_html=True)
        st.subheader("🐂 Bull Case (25% probability)")
        col1, col2, col3 = st.columns(3)
        col1.metric("Conversion Rate", f"{data['financial_model']['bull']['conversion']}%")
        col2.metric("ARR Potential", data['financial_model']['bull']['arr'])
        col3.metric("Payback Period", data['financial_model']['bull']['payback'])
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Bear Case
        st.markdown('<div class="fin-model-section bear-case">', unsafe_allow_html=True)
        st.subheader("🐻 Bear Case (25% probability)")
        col1, col2, col3 = st.columns(3)
        col1.metric("Conversion Rate", f"{data['financial_model']['bear']['conversion']}%")
        col2.metric("ARR Potential", data['financial_model']['bear']['arr'])
        col3.metric("Payback Period", data['financial_model']['bear']['payback'])
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.divider()
        
        # Comparison to targets
        col1, col2 = st.columns(2)
        col1.metric("Target CAC", f"${max_cac}", delta=f"Current: ${TROPHI_OPERATING_MODEL['metrics']['cac']}")
        col2.metric("Target LTV", TROPHI_OPERATING_MODEL['metrics']['ltv'], delta=f"Model: ${data['revenue_potential']['ltv']}")
        
        if int(data['financial_model']['base']['payback'].split()[0]) > 90:
            st.error("❌ **Payback Exceeds Target**: >90 days in base case")
        else:
            st.success("✅ **Payback Acceptable**: Meets <90 day threshold")
    
    with tab_dev:
        st.subheader("Engineering Capacity Impact Analysis")
        
        st.markdown('<div class="dev-impact-card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Hours Required", f"{data['dev_impact']['hours_required']}h")
            st.metric("Sprint Capacity Used", f"{data['dev_impact']['sprint_capacity_pct']}%")
        with col2:
            st.metric("Fully-Loaded Cost", data['dev_impact']['cost_at_120_hr'])
            st.metric("Timeline Impact", f"{data['technical_feasibility']['timeline_days']} days")
        
        if not data['dev_impact']['parallelizable']:
            st.error(f"❌ **Capacity Crisis**: Blocks all other integrations")
            st.warning(f"**Cost to De-Risk**: Contractor at $150/hr = ${data['dev_impact']['hours_required']*150/1000:.1f}K")
        else:
            st.success(f"✅ **Pipeline Optimized**: Can parallelize with 1 other initiative")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.divider()
        
        # Runway impact
        st.subheader("Company Runway Impact")
        monthly_burn = 85000
        integration_cost = int(data['dev_impact']['cost_at_120_hr'].split('$')[1].replace('K','000'))
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Current Runway", "38 months", f"${monthly_burn*38/1_000_000:.1f}M total")
        col2.metric("Integration Cost", data['dev_impact']['cost_at_120_hr'])
        col3.metric("Runway Impact", f"{integration_cost/monthly_burn:.1%} of monthly burn", "Negligible")
        
        if integration_cost/monthly_burn > 0.10:
            st.warning("⚠️ **High Burn Impact**: >10% of monthly burn - consider phasing")
    
    with tab_strat:
        st.subheader("Strategic Positioning & Competitive Moat")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Strategic Fit Score", f"{data['strategic_fit']['score']}/10")
            st.metric("Alignment", data['strategic_fit']['alignment'])
            st.metric("Velocity", f"{data['strategic_fit']['velocity']}/10")
        with col2:
            st.metric("Moat Strengthening", data['strategic_fit']['moat_benefit'])
        
        st.divider()
        st.subheader("Direct Competitive Landscape")
        for comp in data['strategic_fit']['competitors']:
            st.caption(f"• {comp}")
        
        st.divider()
        st.subheader("A16Z SPEEDRUN Network Effects")
        st.success(f"🚀 {data['strategic_fit']['speedrun_leverage']}")
        st.caption("**Leverage**: Portfolio intro, co-marketing, technical support")
    
    with tab_memo:
        st.subheader("Board of Directors Investment Memo")
        
        # Auto-generate memo
        memo_prompt = f"""<|start_header_id|>system<|end_header_id|>
Write a 600-word investment memo for A16Z partners.

**EXECUTIVE VERDICT:** {'🟢 GREENLIGHT' if data['overall_score'] >= 75 else '🟡 CAUTIOUS' if data['overall_score'] >= 60 else '🔴 KILL'}

**STRUCTURE:**
1. Market: {data['market_attractiveness']['tam']} TAM
2. Tech: {data['technical_feasibility']['hours']}h = {data['technical_feasibility']['team_pct']}% capacity
3. Revenue: {data['financial_model']['base']['arr']} ARR base case
4. Strategy: {data['strategic_fit']['alignment']} fit, velocity {data['strategic_fit']['velocity']}/10
5. Dev Impact: {data['dev_impact']['runway_impact']} runway impact
6. Recommendation: {'Execute' if data['overall_score'] >= 75 else 'Defer' if data['overall_score'] >= 60 else 'Reject'}

Include specific numbers, sources, and 30-day action plan.<|eot_id|><|start_header_id|>user<|end_header_id|>
Draft memo.<|eot_id_id|><|start_header_id|>assistant<|end_header_id|>"""
        
        if not st.session_state.memo_text:
            memo = client.chat_completion(model="meta-llama/Llama-3.2-1B-Instruct", messages=[{"role": "user", "content": memo_prompt}], max_tokens=1200, temperature=0.3)
            st.session_state.memo_text = memo.choices[0].message.content
        
        st.markdown(st.session_state.memo_text)

# === FOOTER ===
st.divider()
st.caption("📊 **Trophi.ai Confidential** | A16Z SPEEDRUN Portfolio | Built with Hugging Face Inference API")
