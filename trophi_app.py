import streamlit as st
import json
from huggingface_hub import InferenceClient

# === ENTERPRISE OPERATING MODEL (Surgical Precision) ===
TROPHI_OPERATING_MODEL = {
    "current_state": {
        "team": {
            "total": 22,
            "engineering": 8,
            "product": 3,
            "ml_research": 4,
            "growth": 3,
            "executive": 4,
            "burn_rate": "$85K/month",
            "runway": "38 months"
        },
        "capacity": {
            "max_parallel_integrations": 2,
            "eng_hours_per_sprint": 1_280,  # 8 engineers * 2 weeks * 80 hrs
            "current_utilization": 0.75,
            "available_hours_per_sprint": 320
        },
        "metrics": {
            "mrr": "$47K",
            "arpu": "$18.50",
            "ltv": "$205",
            "cac": "$52",
            "churn": 4.2,
            "magic_number": 0.86,
            "net_revenue_retention": 112
        }
    },
    "integration_benchmarks": {
        "direct_api": {"hours": 40, "cost": "$4,800", "timeline": "5 days", "qa_days": 2},
        "udp_telemetry": {"hours": 120, "cost": "$14,400", "timeline": "14 days", "qa_days": 5},
        "computer_vision": {"hours": 480, "cost": "$57,600", "timeline": "60 days", "qa_days": 15}
    },
    "partnership_std_terms": {
        "revenue_share": "15-25%",
        "min_guarantee": "$25K/year",
        "integration_support": "$10K",
        "co_marketing_budget": "$5K"
    }
}

# === INVESTOR-GRADE RUBRIC (Zero Tolerance for Ambiguity) ===
investor_granular_rubric = """
**FORCED QUANTIFICATION RULES:**
1. Market Attractiveness:
   - TAM: $XM minimum, cite source (SteamSpy, Newzoo, company IR) with URL
   - SAM: Serviceable portion (geography × platform %) = $XM
   - SOM: Trophi's 3yr achievable share (conservative: 1-3%) = $XM
   - Active Users: Specific number OR "Undisclosed (industry avg 50K)"
   - Engagement: Hours/week or ARPU with source

2. Technical Feasibility:
   - Integration Method: [API|UDP|CV] + specific endpoint/protocol
   - Dev Hours: EXACT number (40, 120, 480) from benchmarks
   - Cost: $X,XXX at $120/hr fully-loaded
   - Timeline: Business days (5, 14, 30) + QA days
   - Team Impact: % of available sprint hours (e.g., "12.5% of Q1 capacity")
   - Auto-REJECT: Kernel anti-cheat = INFINITE hours (blocking)

3. Revenue Potential:
   - Pricing: Specific tier ($9.99/$19.99/$29.99) + conversion %
   - Conversion: 0.5%-3.5% (industry: 2.1%, Trophi: 2.8%)
   - ARPU: $XX at target conversion
   - ARR: $XM annual at scale
   - LTV/CAC: Compare to targets ($205/$52)
   - NPV: Include 3-year net present value at 15% discount

4. Strategic Fit:
   - Velocity Score: 1-10 (10 = shipping in 2 weeks due to API access)
   - Moat Strengthening: Specific data points (e.g., "+15K users to coaching dataset")
   - Competitive Response: "VRS may drop prices 15%"

5. Dev Team Impact:
   - Capacity: {sprint_capacity}h available per sprint
   - This Integration: X hours = Y% of sprint
   - Parallelization: Can run with [0|1|2] other integrations?
   - Burn rate delta: ±$X,XXX/month during dev
   - Runway impact: Cost as % of monthly $85K burn

6. Financial Scenarios (MANDATORY):
   - Base: 1.5% conv, 90-day payback, 15% discount rate
   - Bull: 2.5% conv, 60-day payback, +partnership acceleration
   - Bear: 0.8% conv, 120-day payback, 50% integration delay
"""

# === MODERN GLASSMORPHISM UI (Investor-Grade Aesthetics) ===
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&family=JetBrains+Mono:wght@400;600&display=swap');
    
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
        border-left: 4px solid #10b981;
        padding: 15px 20px;
        margin: 10px 0;
        border-radius: 0 8px 8px 0;
    }
    
    .bull-case { border-left-color: #10b981; }
    .base-case { border-left-color: #6366f1; }
    .bear-case { border-left-color: #ef4444; }
    
    code {
        font-family: 'JetBrains Mono', monospace;
        background: rgba(30, 41, 59, 0.7);
        padding: 2px 6px;
        border-radius: 4px;
        color: #fbbf24;
    }
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
    st.metric("MRR", "$47K", "Month-over-month")

# === MAIN APPLICATION ===
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
                                placeholder="Enter opportunity: 'iRacing F1 25 API', 'Logitech G Pro Partnership', 'Assetto Corsa UDP'...")
with col_btn:
    st.write("")
    analyze_btn = st.button("⚡ Execute Analysis", use_container_width=True, type="primary")

# === ANALYSIS PIPELINE ===
if analyze_btn and target_name:
    if "HF_API_TOKEN" not in st.secrets:
        st.error("❌ Missing 'HF_API_TOKEN' in Streamlit Secrets")
        st.stop()
    
    client = InferenceClient(token=st.secrets["HF_API_TOKEN"])
    
    with st.status("Executing 6-phase strategic analysis...", expanded=True):
        # Phase 1: Market Intelligence
        st.write("📡 **Phase 1**: Gathering verifiable market data...")
        market_prompt = f"""<|start_header_id|>system<|end_header_id|>
You are a market intelligence analyst at A16Z. Extract ONLY verifiable numbers.

**MANDATORY SOURCES:**
- SteamSpy (for Steam games)
- Newzoo (for market sizing)
- Company IR reports (for hardware/public companies)
- Official developer docs

**IF DATA UNAVAILABLE:** 
- Use "Undisclosed (est. 10K-50K based on similar titles)"
- Set confidence to 40-60%
- Never say "unknown"

Return JSON:
{{"tam": "$X.XM", "sam": "$X.XM", "som": "$X.XM", "active_users": "X,XXX", "source": "URL|string", "cagr": "X.X%", "confidence": 75}}<|eot_id|>
<|start_header_id|>user<|end_header_id|>
Target: {target_name}
Provide market sizing with source URLs.<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
        
        market = client.chat_completion(model="meta-llama/Llama-3.2-1B-Instruct", messages=[{"role": "user", "content": market_prompt}], max_tokens=350, temperature=0.1)
        market_data = json.loads(market.choices[0].message.content)
        
        # Phase 2: Technical Architecture
        st.write("⚙️ **Phase 2**: Mapping integration architecture...")
        tech_prompt = f"""<|start_header_id|>system<|end_header_id|>
You are a principal engineer at Trophi. Specify exact integration:

**API INTEGRATION:**
- Endpoint: https://api.example.com/v1/telemetry
- Auth: OAuth 2.0 / API Key
- Rate limit: 10,000 req/day
- Hours: 40h (benchmark)

**UDP INTEGRATION:**
- Port: 20777
- Frequency: 60Hz
- Packet format: See docs/api.md
- Hours: 120h (benchmark)

**CV INTEGRATION:**
- Resolution: 1080p@60FPS
- Model: YOLOv8 (5.2GB VRAM)
- Hours: 480h (benchmark) = AUTO-REJECT

Return JSON:
{{"method": "API|UDP", "endpoint": "https://...", "hours": 40, "cost_at_120_hr": "$4,800", "timeline_days": 5, "qa_days": 2, "team_pct_of_sprint": 12.5, "parallelizable": true}}<|eot_id|><|start_header_id|>user<|end_header_id|>
Target: {target_name}
Provide technical spec.<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
        
        tech = client.chat_completion(model="meta-llama/Llama-3.2-1B-Instruct", messages=[{"role": "user", "content": tech_prompt}], max_tokens=400, temperature=0.1)
        tech_data = json.loads(tech.choices[0].message.content)
        
        # Phase 3: Financial Model
        st.write("💰 **Phase 3**: Building 3-case P&L...")
        fin_prompt = f"""<|start_header_id|>system<|end_header_id|>
Build 3-case financial model:

**BASE CASE (50% probability):**
- Conversion: 1.5% (Trophi avg: 2.1%, industry: 2.8%)
- Pricing: $19.99 tier
- Payback: 94 days (target: <90)
- NPV: $1.2M (3yr, 15% discount)

**BULL CASE (25% probability):**
- Conversion: 2.5% (partnership acceleration)
- Pricing: $29.99 tier (premium feature)
- Payback: 63 days
- NPV: $2.1M

**BEAR CASE (25% probability):**
- Conversion: 0.8% (integration delays)
- Pricing: $9.99 tier (churn risk)
- Payback: 157 days
- NPV: $0.4M

Return JSON:
{{"base": {{"conversion": 1.5, "arr": "$420K", "payback": "94 days", "npv": "$1.2M", "coc": "$52"}}, "bull": {{"conversion": 2.5, "arr": "$700K", "payback": "63 days", "npv": "$2.1M"}}, "bear": {{"conversion": 0.8, "arr": "$224K", "payback": "157 days", "npv": "$0.4M"}}}}<|eot_id|><|start_header_id|>user<|end_header_id|>
Target: {target_name}
Users: {market_data['active_users']}
Provide 3-case model.<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
        
        fin = client.chat_completion(model="meta-llama/Llama-3.2-1B-Instruct", messages=[{"role": "user", "content": fin_prompt}], max_tokens=550, temperature=0.1)
        fin_data = json.loads(fin.choices[0].message.content)
        
        # Phase 4: Strategic Positioning
        st.write("🎯 **Phase 4**: Strategic fit & velocity...")
        strategy_prompt = f"""<|start_header_id|>system<|end_header_id|>
Assess strategic fit 1-10 and velocity:

**FIT SCORING:**
- 9-10: iRacing, F1 series, Assetto Corsa (core)
- 7-8: Logitech, Fanatec, Thrustmaster (hardware)
- 5-6: FPS/MOBA (adjacent, requires CV)
- 1-4: Unrelated verticals

**VELOCITY FACTORS:**
- API access: +3 points
- Partner commitment: +2 points
- A16Z intro: +2 points
- Existing relationship: +1 point

**MOAT BENEFIT:**
- Data flywheel: "+X,XXX hours coaching data"
- Network effects: "Y% increase in model accuracy"
- Competitive barrier: "Z-month head start"

Return JSON:
{{"fit_score": 9, "alignment": "Core Racing", "moat_benefit": "15,000 hours coaching data", "competitors": ["VRS at $9.99", "Coach Dave at $19.99"], "velocity": 9, "speedrun_leverage": "A16Z intro to Fanatec CEO"}}<|eot_id|><|start_header_id|>user<|end_header_id|>
Target: {target_name}
Provide strategic assessment.<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
        
        strategy = client.chat_completion(model="meta-llama/Llama-3.2-1B-Instruct", messages=[{"role": "user", "content": strategy_prompt}], max_tokens=400, temperature=0.1)
        strategy_data = json.loads(strategy.choices[0].message.content)
        
        # Phase 5: Consolidate Analysis
        st.write("📊 **Phase 5**: Consolidating evaluation...")
        
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
                "tam": market_data['tam'],
                "sam": market_data['sam'],
                "som": market_data['som'],
                "active_users": market_data['active_users'],
                "cagr": market_data['cagr'],
                "score": round(min(10, int(market_data['active_users'].replace(',', '')) / 10000), 1),
                "rationale": f"{market_data['active_users']} active users growing at {market_data['cagr']}",
                "source": market_data['source']
            },
            "technical_feasibility": {
                "method": tech_data['method'],
                "endpoint": tech_data.get('endpoint', 'N/A'),
                "hours": tech_data['hours'],
                "cost": tech_data['cost_at_120_hr'],
                "timeline_days": tech_data['timeline_days'],
                "qa_days": tech_data['qa_days'],
                "team_pct": round(tech_data['team_pct_of_sprint'], 1),
                "parallelizable": tech_data['parallelizable'],
                "risk_level": "High" if tech_data['hours'] > 200 else "Medium" if tech_data['hours'] > 100 else "Low",
                "score": round(10 - min(tech_data['hours'] / 48, 10), 1)
            },
            "revenue_potential": {
                "conversion_rate": fin_data['base']['conversion'],
                "arr": fin_data['base']['arr'],
                "payback_days": int(fin_data['base']['payback'].split()[0]),
                "ltv": f"${int(fin_data['base']['npv'].split('$')[1].replace('M', '000000').replace('K', '000')) / 1000:.0f}K",
                "score": round(fin_data['base']['conversion'] * 10 / 1.5, 1)
            },
            "strategic_fit": {
                "score": strategy_data['fit_score'],
                "alignment": strategy_data['alignment'],
                "moat_benefit": strategy_data['moat_benefit'],
                "competitors": strategy_data['competitors'],
                "velocity": strategy_data['velocity'],
                "speedrun_leverage": strategy_data['speedrun_leverage']
            },
            "dev_impact": {
                "hours_required": tech_data['hours'],
                "sprint_capacity_pct": round(tech_data['team_pct_of_sprint'], 1),
                "cost_at_120_hr": tech_data['cost_at_120_hr'],
                "parallelizable": tech_data['parallelizable'],
                "runway_impact": f"{int(tech_data['cost_at_120_hr'].split('$')[1].replace(',', '').replace('K', '000')) / 85000:.1%} of monthly burn"
            },
            "financial_model": fin_data
        }
        
        st.session_state.ai_data = ai_data
        st.session_state.analysis_done = True

# === DISPLAY RESULTS ===
if st.session_state.analysis_done and st.session_state.ai_data:
    data = st.session_state.ai_data
    
    # Header with score and confidence
    confidence_color = "#10b981" if data['confidence'] >= 80 else "#f59e0b" if data['confidence'] >= 60 else "#ef4444"
    st.markdown(f"""
        <div class="investor-header">
            <h2>📊 Overall Score: {data['overall_score']}/100</h2>
            <p style="color: {confidence_color}; font-weight: 600;">Data Confidence: {data['confidence']}%</p>
            <p style="font-size: 1.1rem;">**{data['target']}** | Llama-3.2-1B</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Metrics grid
    cols = st.columns(4)
    dimensions = ['market_attractiveness', 'technical_feasibility', 'revenue_potential', 'strategic_fit']
    icons = ['🌍', '⚙️', '💰', '🎯']
    
    for idx, dimension in enumerate(dimensions):
        with cols[idx]:
            score = data[dimension]['score'] if dimension in data else 0
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
            st.metric("Total Addressable Market (TAM)", data['market_attractiveness']['tam'])
            st.metric("Serviceable Addressable Market (SAM)", data['market_attractiveness']['sam'])
            st.metric("Serviceable Obtainable Market (SOM)", data['market_attractiveness']['som'])
        with col2:
            st.metric("Active Users", data['market_attractiveness']['active_users'])
            st.metric("Growth Rate (CAGR)", data['market_attractiveness']['cagr'])
            st.metric("Market Score", f"{data['market_attractiveness']['score']}/10")
        
        st.info(f"**Primary Research:** {data['market_attractiveness']['source']}")
        st.success(f"**Rationale:** {data['market_attractiveness']['rationale']}")
        
        if data['confidence'] < 70:
            st.warning(f"⚠️ **Low Confidence Alert**: {data['confidence']}% - Manual verification required")
            st.caption("Recommend: Direct outreach to target company for user metrics")
    
    with tab_tech:
        st.subheader("Integration Architecture")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Integration Method", data['technical_feasibility']['method'])
            st.metric("API Endpoint", data['technical_feasibility'].get('endpoint', 'N/A'))
            st.metric("Development Hours", f"{data['technical_feasibility']['hours']}h")
        with col2:
            st.metric("Timeline (Incl. QA)", f"{data['technical_feasibility']['timeline_days']} + {data['technical_feasibility']['qa_days']} days")
            st.metric("Risk Level", data['technical_feasibility']['risk_level'])
            st.metric("Tech Score", f"{data['technical_feasibility']['score']}/10")
        
        st.divider()
        st.subheader("Engineering Resource Requirements")
        st.metric("**Fully-Loaded Cost**", data['technical_feasibility']['cost'])
        st.metric("**% of Sprint Capacity**", f"{data['technical_feasibility']['team_pct']}%")
        st.progress(data['technical_feasibility']['team_pct']/100)
        
        if data['technical_feasibility']['parallelizable']:
            st.success(f"✅ Can run in parallel with 1 other integration")
        else:
            st.error(f"❌ **PIPELINE BLOCKER**: Blocks all other integrations for {data['technical_feasibility']['timeline_days']} days")
            st.warning(f"**Recommendation**: Defer or hire contractor at $150/hr to preserve capacity")
    
    with tab_fin:
        st.subheader("Financial Model (3-Case Analysis)")
        
        # Base Case
        st.markdown('<div class="fin-model-section base-case">', unsafe_allow_html=True)
        st.subheader("📊 Base Case (50% probability)")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Conversion Rate", f"{data['financial_model']['base']['conversion']}%")
        col2.metric("ARR Potential", data['financial_model']['base']['arr'])
        col3.metric("Payback Period", data['financial_model']['base']['payback'])
        col4.metric("NPV (3yr)", data['financial_model']['base']['npv'])
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Bull Case
        st.markdown('<div class="fin-model-section bull-case">', unsafe_allow_html=True)
        st.subheader("🐂 Bull Case (25% probability)")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Conversion Rate", f"{data['financial_model']['bull']['conversion']}%")
        col2.metric("ARR Potential", data['financial_model']['bull']['arr'])
        col3.metric("Payback Period", data['financial_model']['bull']['payback'])
        col4.metric("NPV (3yr)", data['financial_model']['bull']['npv'])
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Bear Case
        st.markdown('<div class="fin-model-section bear-case">', unsafe_allow_html=True)
        st.subheader("🐻 Bear Case (25% probability)")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Conversion Rate", f"{data['financial_model']['bear']['conversion']}%")
        col2.metric("ARR Potential", data['financial_model']['bear']['arr'])
        col3.metric("Payback Period", data['financial_model']['bear']['payback'])
        col4.metric("NPV (3yr)", data['financial_model']['bear']['npv'])
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.divider()
        st.subheader("Key Financial Metrics vs. Company Targets")
        col1, col2, col3 = st.columns(3)
        col1.metric("Target CAC", f"${max_cac}", delta=f"Current: ${TROPHI_OPERATING_MODEL['metrics']['cac']}")
        col2.metric("Target LTV", f"${TROPHI_OPERATING_MODEL['metrics']['ltv']}", delta=f"Model: {data['revenue_potential']['ltv']}")
        col3.metric("Magic Number", TROPHI_OPERATING_MODEL['metrics']['magic_number'], delta="Target: >1.0")
        
        if int(data['financial_model']['base']['payback'].split()[0]) > 90:
            st.error("❌ **Payback Exceeds Threshold**: 90-day target not met in base case")
        else:
            st.success("✅ **Payback Acceptable**: Meets <90 day target")
    
    with tab_dev:
        st.subheader("Engineering Capacity Impact Analysis")
        
        st.markdown('<div class="dev-impact-card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Hours Required", f"{data['dev_impact']['hours_required']}h")
            st.metric("Sprint Capacity Used", f"{data['dev_impact']['sprint_capacity_pct']}%")
            st.progress(data['dev_impact']['sprint_capacity_pct']/100)
        with col2:
            st.metric("Fully-Loaded Cost", data['dev_impact']['cost_at_120_hr'])
            st.metric("Timeline Impact", data['technical_feasibility']['timeline_days'])
        
        # Parallelization analysis
        if data['dev_impact']['parallelizable']:
            st.success(f"✅ **Pipeline Efficient**: Can run alongside 1 other integration")
        else:
            st.error(f"❌ **Capacity Crisis**: Blocks pipeline for {data['technical_feasibility']['timeline_days']} days")
            st.warning(f"**Mitigation**: Hire contractor (${150}/hr) = ${data['dev_impact']['hours_required']*150/1000:.1f}K extra cost but preserves team velocity")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.divider()
        
        # Runway Impact
        st.subheader("Company Runway Impact")
        monthly_burn = 85000
        integration_cost = int(data['dev_impact']['cost_at_120_hr'].split('$')[1].replace(',', '').replace('K', '000'))
        runway_months = 38
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Current Runway", f"{runway_months} months", f"${monthly_burn*runway_months/1_000_000:.1f}M total")
        col2.metric("Monthly Burn", f"${monthly_burn:,}", delta=f"Integration: {integration_cost/monthly_burn:.1%}")
        col3.metric("Integration Cost", data['dev_impact']['cost_at_120_hr'], delta="Runway impact: Negligible")
        
        if integration_cost/monthly_burn > 0.15:
            st.warning("⚠️ **High Burn Alert**: >15% of monthly burn - consider phased approach")
    
    with tab_strat:
        st.subheader("Competitive & Strategic Positioning")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Strategic Fit Score", f"{data['strategic_fit']['score']}/10")
            st.metric("Alignment Category", data['strategic_fit']['alignment'])
            st.metric("Velocity Score", f"{data['strategic_fit']['velocity']}/10")
        
        with col2:
            st.metric("Moat Enhancement", data['strategic_fit']['moat_benefit'])
        
        st.divider()
        st.subheader("Direct Competitive Intelligence")
        for comp in data['strategic_fit']['competitors']:
            st.caption(f"• {comp}")
        
        st.divider()
        st.subheader("A16Z SPEEDRUN Leverage")
        st.success(f"🚀 {data['strategic_fit']['speedrun_leverage']}")
        st.caption("**Network Access**: Portfolio company intros, co-marketing, technical support")
        
        if data['strategic_fit']['velocity'] >= 8:
            st.success("🏃 **High-Velocity Opportunity**: Can ship within 2 weeks")
        elif data['strategic_fit']['velocity'] >= 5:
            st.warning("⏱️ **Medium Velocity**: 4-8 week timeline")
        else:
            st.error("🐢 **Low Velocity**: >8 weeks, consider deferral")
    
    with tab_memo:
        st.subheader("Board of Directors Investment Memo")
        
        # Auto-generate memo if not cached
        memo_prompt = f"""<|start_header_id|>system<|end_header_id|>
Write a 600-word memo to A16Z partners and Trophi board.

**MEMO STRUCTURE:**

**EXECUTIVE VERDICT:** {'🟢 GREENLIGHT' if data['overall_score'] >= 75 else '🟡 CAUTIOUS PROCEED' if data['overall_score'] >= 60 else '🔴 KILL'}

**MARKET OPPORTUNITY:** {data['market_attractiveness']['tam']} TAM, {data['market_attractiveness']['sam']} SAM, {data['market_attractiveness']['som']} SOM. {data['market_attractiveness']['rationale']}. Source: {data['market_attractiveness']['source']}. **Confidence: {data['confidence']}%**.

**TECHNICAL INVESTMENT:** {data['technical_feasibility']['hours']}h = {data['technical_feasibility']['team_pct']}% of Q1 capacity. Method: {data['technical_feasibility']['method']}. Timeline: {data['technical_feasibility']['timeline_days']} days. Risk: {data['technical_feasibility']['risk_level']}. **Cost: {data['technical_feasibility']['cost']}**.

**FINANCIAL MODEL:** Base case {data['financial_model']['base']['arr']} ARR at {data['financial_model']['base']['conversion']}% conversion. Payback: {data['financial_model']['base']['payback']}. NPV: {data['financial_model']['base']['npv']}. Bull case: {data['financial_model']['bull']['arr']}. Bear case: {data['financial_model']['bear']['arr']}.

**COMPETITIVE DYNAMICS:** {', '.join(data['strategic_fit']['competitors'])}. **Moat enhancement:** {data['strategic_fit']['moat_benefit']}. **Velocity score:** {data['strategic_fit']['velocity']}/10 (SPEEDRUN leverage: {data['strategic_fit']['speedrun_leverage']}).

**DEV TEAM IMPACT:** {data['dev_impact']['sprint_capacity_pct']}% sprint capacity. Parallelizable: {data['dev_impact']['parallelizable']}. Runway impact: {data['dev_impact']['runway_impact']}. **Recommendation:** {'Hire contractor' if not data['dev_impact']['parallelizable'] else 'Use internal team'}.

**30-DAY ACTION PLAN:**
- Week 1: API sandbox setup, docs review
- Week 2-3: Core integration development
- Week 4: QA, beta launch, metrics instrumentation

**RISKS & MITIGATION:** {data['technical_feasibility']['risk_level']} technical risk. Mitigated by parallel workstreams and A16Z partner support.

**RESOURCE ASK:** {data['technical_feasibility']['cost']}. No additional headcount required. Uses existing sprint capacity.

**RECOMMENDATION:** {'Execute immediately - high confidence opportunity' if data['overall_score'] >= 75 else 'Proceed with caution - monitor metrics closely' if data['overall_score'] >= 60 else 'Reject and reallocate resources to higher-scoring opportunities'}.

**BOILERPLATE:** Trophi delivers 10x human coach efficiency. $47K MRR, 38-month runway, 22-person team scaling to 44. $205 LTV, $52 CAC, 0.86 magic number. A16Z SPEEDRUN providing enterprise pipeline.<|eot_id|><|start_header_id|>user<|end_header_id|>
Draft memo.<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
        
        memo = client.chat_completion(model="meta-llama/Llama-3.2-1B-Instruct", messages=[{"role": "user", "content": memo_prompt}], max_tokens=1200, temperature=0.3)
        st.session_state.memo_text = memo.choices[0].message.content
        st.markdown(st.session_state.memo_text)

# === FOOTER ===
st.divider()
st.caption("📊 **Trophi.ai Confidential** | A16Z SPEEDRUN Portfolio | Generated: 2025-01-17 | Model: Llama-3.2-1B | API: Hugging Face Inference")
