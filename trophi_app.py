import streamlit as st
import json
import time
from huggingface_hub import InferenceClient

# --- COMPANY & MARKET RESEARCH CONTEXT ---
TROPHI_CONTEXT = """
# Trophi.ai Company Intelligence
- **Mission**: Democratize elite-level coaching through AI, making high-performance training accessible regardless of location or income
- **Founded**: December 2021 by Mike Winter (CEO, Memorial University) and Scott Mansell (ex-pro racer)
- **HQ**: St. John's, Newfoundland, Canada
- **Team**: 22 AI/ML experts, software engineers, data scientists; doubling to 44 by EOY 2025
- **Funding**: £3.3M Seed (Build Ventures, 2024) + $548K CAD grants (ACOA, NRC-IRAP)
- **Achievement**: Delivered 125 years of equivalent human coaching in 6 months
- **Validation**: Accepted into A16Z GAMES SPEEDRUN (1% acceptance rate, Winter 2025 cohort)

# Core Technology & Capabilities
- **Primary Data Source**: UDP telemetry streams from racing simulators
- **Anti-Cheat Strategy**: Avoid kernel-level AC; focus on post-race analysis and API-based real-time
- **Integration Methods**: Direct API/SDK > UDP parsing > Computer Vision (last resort)
- **Platform**: Cloud-based SaaS with real-time AI coaching agents
- **Key Metrics**: Sub-second latency, 95%+ accuracy vs human elite coaches

# Target Market Segments
1. **Virtual Racing** (Current Core): iRacing, F1 series, Assetto Corsa Competizione
2. **Esports** (Expansion): FPS, MOBA (requires CV, higher tech lift)
3. **Real-World Sports** (Future): Motorsport telemetry, athlete biomechanics
4. **Industrial/Military** (Long-term): Heavy equipment, tactical training

# Market Intelligence
- **Racing Sim Market**: $0.87B USD (2024) → $1.24B (2029), 7.3% CAGR
- **Virtual Sports Market**: $0.97B (2024) → $1.96B (2033), 8.1% CAGR  
- **iRacing User Base**: ~450 avg concurrent, 1,900 peak, 85.8% positive reviews
- **Key Demographic**: 21-35 years (millennial/Gen Z crossover)
- **Geography**: NA = 40% market share, EU = 35%, APAC = fastest growth

# Competitive Landscape
- **Direct**: Coach Dave Academy, VRS Coaching, Craig's Setup Shop
- **Adjacent**: NVIDIA Omniverse, AWS SimSpace Weaver
- **Threat**: Games launching native AI coaching features
- **Moat**: Speed to market via A16Z network + 125yr coaching data advantage

# Pricing & Business Model
- **Current**: $9.99-29.99/month SaaS (individual), custom B2B licensing
- **Partnership**: Hardware integrations (e.g., Logitech, Fanatec) → zero tech lift, revenue share
- **LTV Goal**: $180+ average subscriber LTV
- **CAC Target**: <$45 for < 3-month payback
"""

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Trophi.ai Scale Decision Engine",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLING - Fixed for readability ---
st.markdown("""
    <style>
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stMetric [data-testid="stMetricValue"] {
        color: white !important;
        font-weight: 700;
        font-size: 2.2rem;
    }
    .stMetric [data-testid="stMetricLabel"] {
        color: rgba(255,255,255,0.9) !important;
        font-weight: 500;
    }
    .score-card {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #667eea;
        margin-bottom: 15px;
    }
    .recommendation-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("🧠 Trophi.ai Scale Decision Engine")
st.caption("AI-Powered Opportunity Assessment for Strategic Growth")
st.divider()

# --- SIDEBAR CONFIG ---
with st.sidebar:
    st.subheader("Evaluation Parameters")
    st.markdown("**Weightings:**")
    st.slider("Market Attractiveness", 0, 50, 35, disabled=True)
    st.slider("Technical Feasibility", 0, 50, 25, disabled=True)
    st.slider("Revenue Potential", 0, 50, 25, disabled=True)
    st.slider("Strategic Fit", 0, 50, 15, disabled=True)

# --- SESSION STATE ---
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "ai_data" not in st.session_state:
    st.session_state.ai_data = None
if "memo_text" not in st.session_state:
    st.session_state.memo_text = None

# --- INPUT SECTION ---
col_input, col_btn = st.columns([3, 1])
with col_input:
    target_name = st.text_input("Target Opportunity", placeholder="e.g., 'iRacing F1 24 Integration', 'Logitech G Pro Partnership'")
with col_btn:
    st.write("")
    analyze_btn = st.button("🚀 Run Strategic Analysis", type="primary")

# --- ANALYSIS LOGIC ---
if analyze_btn and target_name:
    if "HF_API_TOKEN" not in st.secrets:
        st.error("❌ Missing 'HF_API_TOKEN' in Streamlit Secrets")
        st.stop()
    
    client = InferenceClient(token=st.secrets["HF_API_TOKEN"])
    st.session_state.client = client

    with st.spinner(f"🔍 Analyzing: **{target_name}**..."):
        try:
            MODEL_NAME = "meta-llama/Llama-3.2-1B-Instruct"
            
            # Advanced prompt with market research & company context
            data_prompt = f"""<|start_header_id|>system<|end_header_id|>
You are the VP of Strategy at Trophi.ai, tasked with evaluating scaling opportunities. Use the following intelligence:

{TROPHI_CONTEXT}

EVALUATION FRAMEWORK - Score 1-10 on:
1. **Market Attractiveness** (35% weight)
   - Active user base size & growth rate
   - Engagement (avg hrs/week)
   - Geographic concentration vs our NA/EU focus
   - Demographic match (21-35 yr core)

2. **Technical Feasibility** (25% weight)
   - 1=Direct API/SDK access
   - 3=UDP telemetry parsing required
   - 5=Kernel anti-cheat = BLOCKING
   - 7=Computer vision needed = AVOID
   - Integration days: <7=10pts, <30=7pts, <90=4pts, >90=1pt

3. **Revenue Potential** (25% weight)
   - Pricing power in segment (WTP)
   - Est. conversion rate (1-5% baseline)
   - LTV potential vs $180 target
   - Partnership value (hw/sw revenue share)

4. **Strategic Fit** (15% weight)
   - Adjacent to racing core (1-3)
   - Brand credibility boost (1-3)
   - Competitive moat building (1-3)
   - Resource efficiency (1-3)

Return ONLY JSON with these keys:
{{"target": "name",
 "overall_score": 0-100,
 "market_attractiveness": {{"score": 1-10, "rationale": "...", "est_users": "number", "cagr": "percentage"}},
 "technical_feasibility": {{"score": 1-10, "rationale": "...", "integration_days": number, "risk_level": "Low|Med|High"}},
 "revenue_potential": {{"score": 1-10, "rationale": "...", "arr_potential": "$XM", "ltv_estimate": "$XXX"}},
 "strategic_fit": {{"score": 1-10, "rationale": "...","alignment": "Core|Adjacent|New"}},
 "key_risks": ["..."],
 "go_to_market": "..."}}<|eot_id|><|start_header_id|>user<|end_header_id|>
Evaluate: {target_name}
Return raw JSON only.<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
            
            response = client.chat_completion(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": data_prompt}],
                max_tokens=600,
                temperature=0.2,
            )
            
            # Parse with robust error handling
            text_data = response.choices[0].message.content
            for pattern in ["```json", "```"]:
                if pattern in text_data:
                    text_data = text_data.split(pattern)[1].replace("```", "").strip()
            
            if "{" in text_data and "}" in text_data:
                text_data = text_data[text_data.find("{"):text_data.rfind("}") + 1]
            
            ai_data = json.loads(text_data)
            
            # Calculate weighted overall score
            market = ai_data["market_attractiveness"]["score"] * 3.5
            tech = ai_data["technical_feasibility"]["score"] * 2.5
            revenue = ai_data["revenue_potential"]["score"] * 2.5
            strategy = ai_data["strategic_fit"]["score"] * 1.5
            
            ai_data["overall_score"] = round(min(100, (market + tech + revenue + strategy)), 1)
            
            st.session_state.ai_data = ai_data
            st.session_state.analysis_done = True
            
            # --- AUTO-GENERATE EXECUTIVE BRIEF ---
            with st.spinner("📝 Generating strategic recommendations..."):
                memo_prompt = f"""<|start_header_id|>system<|end_header_id|>
You are Trophi.ai's VP of Strategy presenting to the CEO and A16Z partners.

DEPLOYMENT PHILOSOPHY:
- Focus on "Land & Expand" from racing core
- Prioritize API-first integrations (< 30 dev days)
- Avoid kernel anti-cheat at all costs
- Target $180+ LTV, <$45 CAC
- Leverage SPEEDRUN network for BD

OUTPUT FORMAT:
**EXECUTIVE VERDICT:** [GREENLIGHT|CAUTIOUS|KILL]
**MARKET OPPORTUNITY:** [2-3 sentences on size/growth]
**TECHNICAL ROADMAP:** [Specific integration steps + timeline]
**REVENUE MODEL:** [Pricing, GTM, partnership leverage]
**KEY RISKS:** [Top 3 mitigated risks]
**RESOURCE ASK:** [Headcount, budget, timeline]
**NEXT 30 DAYS:** [Actionable milestones]<|eot_id|><|start_header_id|>user<|end_header_id|>
Opportunity: {target_name}
Score: {ai_data['overall_score']}/100
Market: {json.dumps(ai_data['market_attractiveness'])}
Tech: {json.dumps(ai_data['technical_feasibility'])}
Revenue: {json.dumps(ai_data['revenue_potential'])}
Strategic Fit: {json.dumps(ai_data['strategic_fit'])}

Draft board-level memo.<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
                
                memo_response = client.chat_completion(
                    model=MODEL_NAME,
                    messages=[{"role": "user", "content": memo_prompt}],
                    max_tokens=800,
                    temperature=0.4,
                )
                
                st.session_state.memo_text = memo_response.choices[0].message.content
                
        except Exception as e:
            st.error(f"Analysis error: {e}")
            if 'text_data' in locals():
                with st.expander("Debug"):
                    st.code(text_data[:500])

# --- DISPLAY RESULTS ---
if st.session_state.analysis_done and st.session_state.ai_data:
    data = st.session_state.ai_data
    
    # Header with score
    st.subheader(f"📊 Opportunity Score: {data['overall_score']}/100")
    st.caption(f"**Target:** {data['target']}")
    
    # Layout columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Metrics grid
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.metric(
                "Market Attractiveness", 
                f"{data['market_attractiveness']['score']}/10",
                delta=data['market_attractiveness'].get('est_users', 'N/A'),
                help="Active users & growth potential"
            )
        with m_col2:
            st.metric(
                "Technical Feasibility", 
                f"{data['technical_feasibility']['score']}/10",
                delta=data['technical_feasibility'].get('risk_level', 'N/A'),
                delta_color="inverse",
                help="1=API easy, 10=avoid"
            )
        
        m_col3, m_col4 = st.columns(2)
        with m_col3:
            st.metric(
                "Revenue Potential", 
                f"{data['revenue_potential']['score']}/10",
                delta=data['revenue_potential'].get('arr_potential', '$0'),
                help="LTV & pricing power"
            )
        with m_col4:
            st.metric(
                "Strategic Fit", 
                f"{data['strategic_fit']['score']}/10",
                delta=data['strategic_fit'].get('alignment', 'N/A'),
                help="Core vs Adjacent"
            )
        
        # Detailed breakdown
        st.divider()
        st.subheader("🎯 Dimensional Analysis")
        
        for dimension in ['market_attractiveness', 'technical_feasibility', 'revenue_potential', 'strategic_fit']:
            with st.expander(f"**{dimension.replace('_', ' ').title()}** (Score: {data[dimension]['score']}/10)"):
                st.write(f"**Rationale:** {data[dimension]['rationale']}")
                if 'est_users' in data[dimension]:
                    st.write(f"**Est. Users:** {data[dimension]['est_users']}")
                if 'cagr' in data[dimension]:
                    st.write(f"**Growth:** {data[dimension]['cagr']}")
                if 'integration_days' in data[dimension]:
                    st.write(f"**Integration:** {data[dimension]['integration_days']} days")
                if 'arr_potential' in data[dimension]:
                    st.write(f"**ARR Potential:** {data[dimension]['arr_potential']}")
    
    with col2:
        # Risk assessment
        st.subheader("⚠️ Key Risks")
        for i, risk in enumerate(data.get('key_risks', [])[:3], 1):
            st.caption(f"{i}. {risk}")
        
        # Go-to-market
        st.subheader("📈 GTM Strategy")
        st.info(data.get('go_to_market', 'N/A'))
        
        # Verdict
        st.subheader("🎯 Verdict")
        if data['overall_score'] >= 75:
            st.success("**GREENLIGHT**")
        elif data['overall_score'] >= 60:
            st.warning("**CAUTIOUS**")
        else:
            st.error("**KILL**")
    
    # Executive Memo
    st.divider()
    st.subheader("📝 Executive Board Memo")
    
    if st.session_state.memo_text:
        st.markdown(st.session_state.memo_text)
    else:
        st.warning("Generating memo...")
    
    # Raw data for debugging
    with st.expander("🔍 Raw Analysis Data"):
        st.json(data)

# --- FOOTER ---
st.divider()
st.caption("Trophi.ai Scale Decision Engine | Powered by Llama-3.2-1B | Data sources: MarketsandMarkets, Straits Research, Steam Analytics")
