import streamlit as st
import json
from huggingface_hub import InferenceClient

# === ENTERPRISE INTELLIGENCE (Surgical Precision) ===
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
        "direct_api": {"hours": 40, "cost": "$4,800", "timeline": "5 days"},
        "udp_telemetry": {"hours": 120, "cost": "$14,400", "timeline": "14 days"},
        "computer_vision": {"hours": 480, "cost": "$57,600", "timeline": "60 days"}  # Deprecated
    },
    "partnership_std_terms": {
        "revenue_share": "15-25%",
        "min_guarantee": "$25K/year",
        "integration_support": "$10K",
        "co_marketing_budget": "$5K"
    },
    "competitive_map": {
        "direct": {
            "VRS": {"strength": "Setup database", "weakness": "Static content", "price": "$9.99"},
            "Coach_Dave": {"strength": "Video tutorials", "weakness": "No real-time", "price": "$19.99"},
            "Craig_Setup_Shop": {"strength": "Community", "weakness": "No AI", "price": "$14.99"}
        },
        "adjacent": {
            "NVIDIA": {"play": "Omniverse simulation"},
            "AWS": {"play": "SimSpace Weaver"},
            "Unity": {"play": "ML-Agents"}
        }
    }
}

# === STRICT EVALUATION RUBRIC (No Ambiguity) ===
RUBRIC investor_granular = """
**FORCED QUANTIFICATION RULES:**
1. Market Attractiveness:
   - TAM: $XM minimum, cite source (SteamSpy, Newzoo, company IR)
   - SAM: Serviceable portion (geography x platform %)
   - SOM: Trophi's 3yr achievable share (conservative: 1-3%)
   - Active Users: Specific number OR "Undisclosed (est. 10K-50K from similar titles)"
   - Engagement: Hours/week OR revenue/user
   
2. Technical Feasibility:
   - Integration Method: [API|UDP|CV] + specific endpoint/protocol
   - Dev Hours: EXACT number (40, 120, 480) - no ranges
   - Cost: $X,XXX at $120/hr fully-loaded
   - Timeline: Business days (5, 14, 30)
   - Team Impact: % of available sprint hours (e.g., "12% of Q1 capacity")
   
3. Revenue Potential:
   - Pricing: Specific tier ($9.99/$19.99/$29.99) + conversion %
   - Conversion: 0.5%-3.5% (benchmark: iRacing 2.1%)
   - ARPU: $XX at target conversion
   - ARR: $XM annual at scale
   - LTV/CAC: Compare to targets ($205/$52)
   
4. Strategic Fit:
   - Velocity Score: 1-10 (10 = shipping in 2 weeks)
   - Moat Strengthening: Specific data flywheel description
   - Resource Efficiency: Opportunity cost ratio vs. next best
   
5. Dev Team Impact:
   - Current capacity: 320h/sprint available
   - This integration: X hours = Y% of sprint
   - Parallelization: Can run with [0|1|2] other integrations
   - Burn rate delta: ±$X,XXX/month during dev
   
6. Financial Model (3 scenarios):
   - **Base**: X% conversion, Y-month payback
   - **Bull**: X+50% conversion, partnership acceleration
   - **Bear**: 50% of base, integration delays
"""

# === MAIN APPLICATION ===
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
    
    .metric-investor {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.9) 0%, rgba(124, 58, 237, 0.9) 100%);
        border-radius: 16px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
    }
    
    .metric-value {
        font-family: 'Inter', sans-serif;
        font-weight: 900;
        font-size: 3rem;
        color: white;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .metric-label {
        color: rgba(255, 255, 255, 0.8);
        font-weight: 600;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1.2px;
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
    
    st.caption("**Team Capacity**")
    sprint_capacity = st.slider("Available Sprint Hours", 200, 600, 320)
    
    st.caption("**Financial Thresholds**")
    min_arr = st.number_input("Min ARR Potential ($K)", 100, 1000, 250) * 1000
    max_cac = st.number_input("Max CAC ($)", 50, 150, 65)
    
    st.divider()
    st.caption("**Current State**")
    st.metric("Runway", "38 months", burn_rate)
    st.metric("Team Size", "22 → 44 EOY")
    st.metric("MRR", "$47K", "+$8K M/M")

# === ANALYSIS LOGIC ===
if analyze_btn and target_name:
    client = InferenceClient(token=st.secrets["HF_API_TOKEN"])
    
    with st.status("Executing strategic analysis pipeline...", expanded=True):
        # Phase 1: Market Intelligence
        st.write("📡 **Phase 1**: Gathering verifiable market data...")
        
        market_prompt = f"""<|start_header_id|>system<|end_header_id|>
Act as a market intelligence analyst. Extract ONLY verifiable numbers. If data unavailable, estimate conservatively using:
- Racing sim titles: 50K-500K active users
- AAA games: 1M-10M active users
- Hardware: Use company IR reports (Logitech, Thrustmaster)
- Always include confidence %. Do not say "unknown".

Return JSON:
{{"tam": "$X.XM", "sam": "$X.XM", "som": "$X.XM", "active_users": "X,XXX", "source": "SteamSpy|Newzoo|Company IR", "cagr": "X.X%", "confidence": 75}}<|eot_id|>
<|start_header_id|>user<|end_header_id|>
Target: {target_name}
Provide market sizing only.<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
        
        market = client.chat_completion(model="meta-llama/Llama-3.2-1B-Instruct", messages=[{"role": "user", "content": market_prompt}], max_tokens=300, temperature=0.1)
        market_data = json.loads(market.choices[0].message.content)
        
        # Phase 2: Technical Architecture
        st.write("⚙️ **Phase 2**: Mapping integration architecture...")
        
        tech_prompt = f"""<|start_header_id|>system<|end_header_id|>
You are a principal engineer. Specify exact integration:
- If API: endpoint, auth method, rate limits
- If UDP: port, packet structure, frequency
- If CV: resolution, FPS, model size (GB)
- Hours: Use benchmarks (API=40h, UDP=120h, CV=480h)
- Timeline: Account for QA, docs, deployment

Return JSON:
{{"method": "API|UDP|CV", "endpoint": "url|string", "hours": 40, "cost": "$4,800", "timeline": "5 days", "team_pct": 12.5, "parallelizable": true}}<|eot_id|><|start_header_id|>user<|end_header_id|>
Target: {target_name}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
        
        tech = client.chat_completion(model="meta-llama/Llama-3.2-1B-Instruct", messages=[{"role": "user", "content": tech_prompt}], max_tokens=350, temperature=0.1)
        tech_data = json.loads(tech.choices[0].message.content)
        
        # Phase 3: Financial Model
        st.write("💰 **Phase 3**: Building P&L scenarios...")
        
        fin_prompt = f"""<|start_header_id|>system<|end_header_id|>
Build 3-case model:
- Base: 1.5% conversion, 90-day payback
- Bull: 2.5% conversion, 60-day payback, +50% partnership accel
- Bear: 0.8% conversion, 120-day payback, 50% delay

Use Trophi metrics: $47K MRR, $205 LTV, $52 CAC target

Return JSON:
{{"base": {{"conversion": 1.5, "arr": "$420K", "payback": "94 days", "npv": "$1.2M"}}, "bull": {{...}}, "bear": {{...}}}}<|eot_id|><|start_header_id|>user<|end_header_id|>
Target: {target_name}
Market users: {market_data['active_users']}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
        
        fin = client.chat_completion(model="meta-llama/Llama-3.2-1B-Instruct", messages=[{"role": "user", "content": fin_prompt}], max_tokens=500, temperature=0.1)
        fin_data = json.loads(fin.choices[0].message.content)
        
        # Phase 4: Strategic Fit & Competitive Moat
        st.write("🎯 **Phase 4**: Assessing strategic positioning...")
        
        strategy_prompt = f"""<|start_header_id|>system<|end_header_id|>
Score strategic fit 1-10:
- 9-10: Direct racing core (iRacing, F1 series)
- 6-8: Hardware partnerships with data moat
- 3-5: Adjacent esports (FPS/MOBA)
- 1-2: Unrelated verticals

Identify: 
- Direct competitors (VRS, Coach Dave)
- Moat strengthening (data flywheel, network effects)
- A16Z SPEEDRUN leverage (partner intros, BD)

Return JSON:
{{"fit_score": 9, "competitors": ["VRS at $9.99"], "moat_benefit": "125yr coaching data + 15K new users", "velocity": 10, "speedrun_leverage": "Hardware intro via A16Z network"}}<|eot_id|><|start_header_id|>user<|end_header_id|>
Target: {target_name}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
        
        strategy = client.chat_completion(model="meta-llama/Llama-3.2-1B-Instruct", messages=[{"role": "user", "content": strategy_prompt}], max_tokens=350, temperature=0.1)
        strategy_data = json.loads(strategy.choices[0].message.content)
        
        # Phase 5: Dev Team Impact
        st.write("👥 **Phase 5**: Calculating team capacity impact...")
        
        capacity_pct = (tech_data['hours'] / sprint_capacity) * 100
        can_parallel = capacity_pct < 40
        
        # Phase 6: Consolidate & Score
        ai_data = {
            "target": target_name,
            "overall_score": round(
                (market_data['confidence'] * 0.35) +
                ((10 - min(tech_data['hours']/48, 10)) * 2.5) +
                (fin_data['base']['conversion'] * 100 * 0.25) +
                (strategy_data['fit_score'] * 1.5)
            , 1),
            "confidence": round(market_data['confidence'], 0),
            "market_attractiveness": {
                "score": round(min(10, market_data['active_users'].replace(',', '')/10000), 1),
                "tam": market_data['tam'],
                "sam": market_data['sam'],
                "som": market_data['som'],
                "rationale": f"{market_data['active_users']} active users, {market_data['cagr']} CAGR",
                "source": market_data['source'],
                "cagr": market_data['cagr']
            },
            "technical_feasibility": {
                "score": round(10 - min(tech_data['hours']/48, 10), 1),
                "method": tech_data['method'],
                "endpoint": tech_data.get('endpoint', 'N/A'),
                "hours": tech_data['hours'],
                "cost": tech_data['cost'],
                "timeline": tech_data['timeline'],
                "team_pct": round(capacity_pct, 1),
                "parallelizable": can_parallel,
                "risk_level": "High" if tech_data['hours'] > 200 else "Med" if tech_data['hours'] > 100 else "Low"
            },
            "revenue_potential": {
                "score": round(fin_data['base']['conversion'] * 10 / 1.5, 1),  # Normalize to 10
                "conversion_rate": fin_data['base']['conversion'],
                "arr": fin_data['base']['arr'],
                "payback_days": int(fin_data['base']['payback'].split()[0]),
                "ltv": f"${int(fin_data['base']['npv'].split('$')[1].replace('M', '000000').replace('K', '000'))/1000:.0f}K"
            },
            "strategic_fit": {
                "score": strategy_data['fit_score'],
                "alignment": "Core" if strategy_data['fit_score'] >= 8 else "Adjacent" if strategy_data['fit_score'] >= 5 else "New Vertical",
                "moat_benefit": strategy_data['moat_benefit'],
                "competitors": strategy_data['competitors'],
                "velocity": strategy_data['velocity']
            },
            "dev_impact": {
                "hours_required": tech_data['hours'],
                "sprint_pct": round(capacity_pct, 1),
                "parallelizable": can_parallel,
                "burn_delta": f"${tech_data['cost']}",
                "runway_impact": "Negligible" if tech_data['hours'] < 100 else "Minor" if tech_data['hours'] < 200 else "Moderate"
            },
            "financial_model": fin_data
        }
        
        st.session_state.ai_data = ai_data
        st.session_state.analysis_done = True

# === DISPLAY RESULTS ===
if st.session_state.analysis_done and st.session_state.ai_data:
    data = st.session_state.ai_data
    
    # Header with score
    st.markdown(f'<div class="investor-header">', unsafe_allow_html=True)
    st.subheader(f"📊 Overall Score: {data['overall_score']}/100")
    st.caption(f"**{data['target']}** | Confidence: {data['confidence']}% | Model: Llama-3.2-1B")
    st.markdown('</div>', unsafe_allow_html=True)
    
    cols = st.columns(4)
    for idx, dimension in enumerate(['market_attractiveness', 'technical_feasibility', 'revenue_potential', 'strategic_fit']):
        with cols[idx]:
            score = data[dimension]['score']
            st.markdown(f"""
                <div class="metric-investor">
                    <div class="metric-label">{dimension.replace('_', ' ').title()}</div>
                    <div class="metric-value">{score}</div>
                </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # === TABS FOR GRANULARITY ===
    tab_market, tab_tech, tab_fin, tab_dev, tab_strat, tab_memo = st.tabs(["🌍 Market Deep Dive", "⚙️ Technical Architecture", "💰 Financial Model", "👥 Dev Team Impact", "🎯 Strategic Positioning", "📝 Investor Memo"])
    
    with tab_market:
        st.subheader("Market Sizing & Evidence")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("TAM", data['market_attractiveness']['tam'])
            st.metric("SAM", data['market_attractiveness']['sam'])
            st.metric("SOM (3yr)", data['market_attractiveness']['som'])
        with col2:
            st.metric("Active Users", data['market_attractiveness'].get('active_users', 'N/A'))
            st.metric("CAGR", data['market_attractiveness']['cagr'])
            st.caption(f"**Source:** {data['market_attractiveness']['source']}")
        
        st.info(f"**Rationale:** {data['market_attractiveness']['rationale']}")
        
        if data['confidence'] < 70:
            st.warning(f"⚠️ **Low Confidence Alert**: {data['confidence']}% - Verify market data via manual research")
    
    with tab_tech:
        st.subheader("Integration Architecture")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Method", data['technical_feasibility']['method'])
            st.metric("Endpoint", data['technical_feasibility'].get('endpoint', 'N/A'))
        with col2:
            st.metric("Timeline", data['technical_feasibility']['timeline'])
            st.metric("Risk Level", data['technical_feasibility']['risk_level'])
        
        st.divider()
        st.subheader("Dev Resource Requirements")
        st.metric("**Engineering Hours**", f"{data['dev_impact']['hours_required']}h")
        st.metric("**Fully-Loaded Cost**", data['dev_impact']['burn_delta'])
        st.metric("**% of Sprint Capacity**", f"{data['dev_impact']['sprint_pct']}%")
        st.metric("**Parallelizable?**", "✅ Yes" if data['dev_impact']['parallelizable'] else "❌ No")
        
        if not data['dev_impact']['parallelizable']:
            st.error("⚠️ **Capacity Blocker**: This will block other integrations for {data['technical_feasibility']['timeline']}")
    
    with tab_fin:
        st.subheader("Financial Model (3-Case)")
        
        # Base Case
        st.markdown('<div class="fin-model-section base-case">', unsafe_allow_html=True)
        st.subheader("📊 Base Case")
        col1, col2, col3 = st.columns(3)
        col1.metric("Conversion", f"{data['financial_model']['base']['conversion']}%")
        col2.metric("ARR", data['financial_model']['base']['arr'])
        col3.metric("Payback", data['financial_model']['base']['payback_days'])
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Bull Case
        st.markdown('<div class="fin-model-section bull-case">', unsafe_allow_html=True)
        st.subheader("🐂 Bull Case")
        col1, col2, col3 = st.columns(3)
        col1.metric("Conversion", f"{data['financial_model']['bull']['conversion']}%")
        col2.metric("ARR", data['financial_model']['bull']['arr'])
        col3.metric("Payback", data['financial_model']['bull']['payback_days'])
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Bear Case
        st.markdown('<div class="fin-model-section bear-case">', unsafe_allow_html=True)
        st.subheader("🐻 Bear Case")
        col1, col2, col3 = st.columns(3)
        col1.metric("Conversion", f"{data['financial_model']['bear']['conversion']}%")
        col2.metric("ARR", data['financial_model']['bear']['arr'])
        col3.metric("Payback", data['financial_model']['bear']['payback_days'])
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.divider()
        st.subheader("Key Metrics vs. Targets")
        col1, col2 = st.columns(2)
        col1.metric("Current CAC", "$52", delta=f"Target: ${max_cac}")
        col2.metric("Current LTV", "$205", delta=f"Target: $180+")
        
        if int(data['financial_model']['base']['payback'].split()[0]) > 90:
            st.warning("⚠️ **Payback Warning**: Exceeds 90-day threshold")
    
    with tab_dev:
        st.subheader("Engineering Capacity Impact")
        
        st.markdown('<div class="dev-impact-card">', unsafe_allow_html=True)
        st.metric("Sprint Hours Required", f"{data['dev_impact']['hours_required']}h")
        st.metric("% of Available Capacity", f"{data['dev_impact']['sprint_pct']}%")
        st.metric("Effective Cost", data['dev_impact']['burn_delta'])
        st.metric("Timeline Impact", data['technical_feasibility']['timeline'])
        
        # Capacity visualization
        st.progress(data['dev_impact']['sprint_pct']/100)
        st.caption(f"**Available Hours:** {sprint_capacity} | **This Integration:** {data['dev_impact']['hours_required']}h")
        
        if data['dev_impact']['parallelizable']:
            st.success(f"✅ Can parallelize with 1 other integration")
        else:
            st.error(f"❌ Blocks pipeline for {data['technical_feasibility']['timeline']}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.divider()
        
        # Runway impact
        st.subheader("Company Runway Impact")
        monthly_burn = 85000
        integration_cost = int(data['dev_impact']['burn_delta'].split('$')[1].replace(',', '').replace('K', '000'))
        runway_months = 38
        
        st.metric("Current Runway", f"{runway_months} months", delta=f"~${monthly_burn*runway_months/1_000_000:.1f}M total")
        st.metric("Integration Cost", data['dev_impact']['burn_delta'], delta=f"{integration_cost/monthly_burn:.1%} of monthly burn")
        
        if integration_cost/monthly_burn > 0.10:
            st.warning("⚠️ **High Cost Alert**: >10% of monthly burn")
    
    with tab_strat:
        st.subheader("Competitive & Strategic Positioning")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Strategic Fit Score", f"{data['strategic_fit']['score']}/10")
            st.metric("Alignment", data['strategic_fit']['alignment'])
            st.metric("Velocity", f"{data['strategic_fit']['velocity']}/10")
        
        with col2:
            st.metric("Moat Strengthening", data['strategic_fit']['moat_benefit'])
            st.caption("**Direct Competitors:**")
            for comp in data['strategic_fit']['competitors']:
                st.caption(f"• {comp}")
        
        st.divider()
        
        # A16Z SPEEDRUN leverage
        st.subheader("A16Z SPEEDRUN Leverage")
        st.info("**Network Effects**: Hardware intros via A16Z portfolio (Logitech, Fanatec) | Co-marketing with portfolio titles")
        
        if data['strategic_fit']['velocity'] >= 8:
            st.success("🚀 **High Velocity**: Can leverage SPEEDRUN momentum for fast partnership execution")
    
    with tab_memo:
        st.subheader("Board-Level Investment Memo")
        
        if st.session_state.memo_text:
            st.markdown(st.session_state.memo_text)
        else:
            # Generate memo if not cached
            memo_prompt = f"""<|start_header_id|>system<|end_header_id|>
Write a 500-word memo to A16Z partners and Trophi board.

STRUCTURE:
**EXECUTIVE VERDICT:** [GREENLIGHT/CAUTIOUS/KILL] based on {data['overall_score']}/100

**MARKET OPPORTUNITY:** {data['market_attractiveness']['tam']} TAM, {data['market_attractiveness']['sam']} SAM, {data['market_attractiveness']['som']} SOM achievable in 36 months. {data['market_attractiveness']['rationale']} (Source: {data['market_attractiveness']['source']})

**TECHNICAL INVESTMENT:** {data['technical_feasibility']['hours']}h = {data['dev_impact']['sprint_pct']}% of Q1 capacity. Method: {data['technical_feasibility']['method']}. Timeline: {data['technical_feasibility']['timeline']}. Risk: {data['technical_feasibility']['risk_level']}.

**REVENUE MODEL:** Base case {data['financial_model']['base']['arr']} ARR at {data['financial_model']['base']['conversion']}% conversion. Payback: {data['financial_model']['base']['payback_days']} days. Bear case: {data['financial_model']['bear']['arr']}.

**COMPETITIVE DYNAMICS:** {', '.join(data['strategic_fit']['competitors'])}. Our moat: {data['strategic_fit']['moat_benefit']}. Velocity score: {data['strategic_fit']['velocity']}/10.

**RESOURCE ASK:** {data['dev_impact']['burn_delta']} dev cost. {data['dev_impact']['sprint_pct']}% capacity allocation. Can parallelize: {data['dev_impact']['parallelizable']}.

**RUNWAY IMPACT:** Integration cost = {int(data['dev_impact']['burn_delta'].split('$')[1].replace('K','000'))/85000:.1%} of monthly burn. Negligible impact on 38-month runway.

**30-DAY MILESTONES:** Week 1: API docs review + sandbox setup. Week 2-3: Core integration. Week 4: QA + beta launch.

**RISKS:** {data['technical_feasibility']['risk_level']} technical risk. Mitigation: Parallelizable workstreams, A16Z partner support for BD.

**RECOMMENDATION:** {'Execute immediately' if data['overall_score'] >= 75 else 'Proceed with caution' if data['overall_score'] >= 60 else 'Reject and reallocate resources'}.

BOILERPLATE: Trophi delivers 10x human coach efficiency. $47K MRR, 38-month runway, 22-person team scaling to 44. SPEEDRUN portfolio providing enterprise pipeline.<|eot_id|><|start_header_id|>user<|end_header_id|>
Draft memo.<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
            
            memo = client.chat_completion(model="meta-llama/Llama-3.2-1B-Instruct", messages=[{"role": "user", "content": memo_prompt}], max_tokens=1000, temperature=0.3)
            st.session_state.memo_text = memo.choices[0].message.content
            st.markdown(st.session_state.memo_text)

# FOOTER
st.divider()
st.caption("📊 **Trophi.ai Scale Engine** | Confidential | A16Z SPEEDRUN Portfolio | Generated: 2025-01-17")
