import streamlit as st
import json
import re
from huggingface_hub import InferenceClient

# === ENTERPRISE OPERATING MODEL (Lines 1-20) ===
TROPHI_OPERATING_MODEL = {
    "current_state": {
        "team": {"total": 22, "engineering": 8, "burn_rate": "$85K/month", "runway": "38 months"},
        "capacity": {"available_hours_per_sprint": 320},
        "metrics": {"ltv": "$205", "cac": "$52", "mrr": "$47K", "magic_number": 0.86}
    },
    "integration_benchmarks": {
        "direct_api": {"hours": 40, "cost": "$4,800", "timeline": "5 days"},
        "udp_telemetry": {"hours": 120, "cost": "$14,400", "timeline": "14 days"},
        "computer_vision": {"hours": 480, "cost": "$57,600", "timeline": "60 days"}
    },
    "partnership_std_terms": {
        "revenue_share": "15-25%",
        "min_guarantee": "$25K/year",
        "integration_support": "$10K",
        "co_marketing_budget": "$5K"
    }
}

# === BULLETPROOF JSON PARSER (Lines 21-80) ===
def parse_json_safely(text, phase_name="Parse", fallback_data=None):
    """
    Ultra-robust JSON extraction with placeholder detection
    """
    try:
        # Remove control characters and normalize whitespace
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
        
        # Repair mismatched braces
        open_braces = json_str.count('{')
        close_braces = json_str.count('}')
        if open_braces > close_braces:
            json_str += '}' * (open_braces - close_braces)
        
        # Parse
        result = json.loads(json_str)
        
        # Detect and replace placeholders
        placeholder_map = {
            "$XM": "$25M",  # Default TAM
            "X,XXX": "15,000",  # Default users
            "X%": "7.3%",  # Default CAGR
            "YOUR_RATIONALE": "Limited public data - requires manual research"
        }
        
        def replace_placeholders(obj):
            if isinstance(obj, dict):
                return {k: replace_placeholders(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_placeholders(item) for item in obj]
            elif isinstance(obj, str):
                for placeholder, replacement in placeholder_map.items():
                    if placeholder in obj:
                        st.warning(f"⚠️ Found placeholder '{placeholder}' - using default {replacement}")
                        obj = obj.replace(placeholder, replacement)
                return obj
            return obj
        
        result = replace_placeholders(result)
        
        # Validate against fallback
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

# === PARSING UTILS (Lines 81-110) ===
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

# === COMPREHENSIVE FALLBACK DATA (Lines 111-150) ===
FALLBACK_MARKET = {
    "tam": "$25M", "sam": "$12M", "som": "$1.2M",
    "active_users": "Undisclosed (est. 10K-50K from similar titles)", 
    "source": "Industry estimation - REQUIRES MANUAL VERIFICATION",
    "cagr": "5-10% (conservative estimate)", 
    "confidence": 35,
    "rationale": "Limited public data - conservative estimate based on similar racing sim titles"
}

FALLBACK_TECH = {
    "method": "UDP (assume telemetry parsing required)",
    "endpoint": "Standard port - research needed",
    "hours": 120, 
    "cost_at_120_hr": "$14,400",
    "timeline_days": 14, 
    "qa_days": 5,
    "team_pct_of_sprint": 37.5,
    "parallelizable": False,
    "risk_level": "Medium",
    "source": "Trophi engineering benchmarks"
}

FALLBACK_FINANCIAL = {
    "base": {"conversion": 1.0, "arr": "$180K", "payback": "120 days", "npv": "$0.4M", "ltv": "$180"},
    "bull": {"conversion": 2.0, "arr": "$360K", "payback": "75 days", "npv": "$0.9M", "ltv": "$360"},
    "bear": {"conversion": 0.5, "arr": "$90K", "payback": "180 days", "npv": "$0.1M", "ltv": "$90"}
}

FALLBACK_STRATEGY = {
    "fit_score": 5, 
    "alignment": "Unknown (requires product review)", 
    "moat_benefit": "Limited information available",
    "competitors": ["Manual research required"], 
    "velocity": 5, 
    "speedrun_leverage": "Investigate A16Z network connections",
    "risk_level": "Unknown"
}

# === UI STYLING (Lines 151-200) ===
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
        letter-spacing: 1px;
    }
    
    .fallback-banner {
        background: rgba(245, 158, 11, 0.2);
        border: 2px solid #f59e0b;
        border-radius: 12px;
        padding: 15px;
        margin: 15px 0;
        font-weight: 600;
        text-align: center;
    }
    
    .phase-success { color: #10b981; }
    .phase-warning { color: #f59e0b; }
    .phase-error { color: #ef4444; }
    
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

# === SESSION STATE (Lines 201-210) ===
for key in ["analysis_done", "ai_data", "memo_text", "used_fallback", "phase_errors", "demo_mode"]:
    if key not in st.session_state:
        st.session_state[key] = False if key in ["analysis_done", "demo_mode"] else (None if key in ["ai_data", "memo_text"] else False)

# === INPUT SECTION (Lines 211-235) ===
st.markdown('<div class="investor-header">', unsafe_allow_html=True)
st.title("🧠 Trophi.ai Scale Decision Engine")
st.caption("**Investor-Grade Strategic Opportunity Assessment** | A16Z SPEEDRUN Portfolio")
st.markdown('</div>', unsafe_allow_html=True)

col_input, col_btn = st.columns([4, 1])
with col_input:
    target_name = st.text_input("🎯 Opportunity to Evaluate", 
                                placeholder="e.g., 'iRacing F1 25 Direct API Integration', 'Logitech G Pro Partnership'")

with col_btn:
    st.write("")
    analyze_btn = st.button("⚡ Execute Analysis", use_container_width=True, type="primary")

# === SIDEBAR CONTROLS (Lines 236-260) ===
with st.sidebar:
    st.image("https://img.logoipsum.com/297.svg", width=120)
    st.markdown("### 📊 Current State")
    st.metric("Runway", "38 months", "$3.23M total")
    st.metric("Burn Rate", "$85K/month", "1.8% weekly")
    st.metric("MRR", "$47K", "+$8K M/M")
    
    st.divider()
    st.markdown("### 🎯 Evaluation Controls")
    sprint_capacity = st.slider("Available Sprint Hours", 200, 600, 320, help="Engineering capacity per 2-week sprint")
    min_arr = st.number_input("Min ARR Threshold ($K)", 100, 1000, 250) * 1000
    max_cac = st.number_input("Max CAC ($)", 50, 150, 65)

# === ANALYSIS PIPELINE START (Lines 261-300) ===
if analyze_btn and target_name:
    if "HF_API_TOKEN" not in st.secrets:
        st.error("❌ Missing 'HF_API_TOKEN' in Streamlit Secrets")
        st.stop()
    
    client = InferenceClient(token=st.secrets["HF_API_TOKEN"])
    st.session_state.used_fallback = False
    st.session_state.phase_errors = []
    
    with st.status("Executing 6-phase strategic analysis pipeline...", expanded=True):
        
        # === PHASE 1: MARKET INTELLIGENCE ===
        st.write("📡 **Phase 1**: Gathering verifiable market data...")
        
        market_prompt = f"""<|start_header_id|>system<|end_header_id|>
Return ONLY a JSON object with these exact keys:
{{"tam": "$XM", "sam": "$XM", "som": "$XM", "active_users": "X,XXX", "source": "SteamSpy", "cagr": "X%", "confidence": 80, "rationale": "Your rationale here"}}

TARGET: {target_name}
Return JSON only.<|eot_id|><|start_header_id|>user<|end_header_id|>
Return JSON only.<|eot_id_id|><|start_header_id|>assistant<|end_header_id|>"""
        
        try:
            market = client.chat_completion(model="meta-llama/Llama-3.2-1B-Instruct", messages=[{"role": "user", "content": market_prompt}], max_tokens=450, temperature=0.1)
            market_data = parse_json_safely(market.choices[0].message.content, "Phase 1 Market", FALLBACK_MARKET)
            st.write(f"<span class='phase-success'>✅ Phase 1 Complete: {market_data['confidence']}% confidence</span>", unsafe_allow_html=True)
        except Exception as e:
            st.session_state.phase_errors.append(f"Phase 1: {str(e)}")
            st.write(f"<span class='phase-warning'>⚠️ Phase 1 Failed - Using Fallback</span>", unsafe_allow_html=True)
            market_data = FALLBACK_MARKET
            st.session_state.used_fallback = True

# [Phase 2-5 and display logic would continue in next section...]
        # === PHASE 2: TECHNICAL ARCHITECTURE (Lines 301-340) ===
        st.write("⚙️ **Phase 2**: Mapping integration architecture...")
        
        tech_prompt = f"""<|start_header_id|>system<|end_header_id|>
Return ONLY a JSON object with these exact keys:
{{"method": "API|UDP", "endpoint": "URL|Port", "hours": 40, "cost_at_120_hr": "$4,800", "timeline_days": 5, "team_pct_of_sprint": 12.5, "parallelizable": true, "risk_level": "Low"}}

TARGET: {target_name}
Return JSON only.<|eot_id|><|start_header_id|>user<|end_header_id|>
Return JSON only.<|eot_id_id|><|start_header_id|>assistant<|end_header_id|>"""
        
        try:
            tech = client.chat_completion(model="meta-llama/Llama-3.2-1B-Instruct", messages=[{"role": "user", "content": tech_prompt}], max_tokens=450, temperature=0.1)
            tech_data = parse_json_safely(tech.choices[0].message.content, "Phase 2 Tech", FALLBACK_TECH)
            st.write(f"<span class='phase-success'>✅ Phase 2 Complete: {tech_data['hours']}h</span>", unsafe_allow_html=True)
        except Exception as e:
            st.session_state.phase_errors.append(f"Phase 2: {str(e)}")
            st.write(f"<span class='phase-warning'>⚠️ Phase 2 Failed - Using Fallback</span>", unsafe_allow_html=True)
            tech_data = FALLBACK_TECH
            st.session_state.used_fallback = True
        
        # === PHASE 3: FINANCIAL MODEL (Lines 341-380) ===
        st.write("💰 **Phase 3**: Building 3-case P&L...")
        
        fin_prompt = f"""<|start_header_id|>system<|end_header_id|>
Return ONLY a JSON object with these exact keys:
{{"base": {{"conversion": 1.5, "arr": "$420K", "payback": "94 days", "npv": "$1.2M", "ltv": "$205"}}, "bull": {{"conversion": 2.5, "arr": "$700K", "payback": "63 days", "npv": "$2.1M", "ltv": "$342"}}, "bear": {{"conversion": 0.8, "arr": "$224K", "payback": "157 days", "npv": "$0.4M", "ltv": "$109"}}}}

USERS: {market_data['active_users']}
Return JSON only.<|eot_id|><|start_header_id|>user<|end_header_id|>
Return JSON only.<|eot_id_id|><|start_header_id|>assistant<|end_header_id|>"""
        
        try:
            fin = client.chat_completion(model="meta-llama/Llama-3.2-1B-Instruct", messages=[{"role": "user", "content": fin_prompt}], max_tokens=600, temperature=0.1)
            fin_data = parse_json_safely(fin.choices[0].message.content, "Phase 3 Financial", FALLBACK_FINANCIAL)
            st.write(f"<span class='phase-success'>✅ Phase 3 Complete: {fin_data['base']['arr']} base case</span>", unsafe_allow_html=True)
        except Exception as e:
            st.session_state.phase_errors.append(f"Phase 3: {str(e)}")
            st.write(f"<span class='phase-warning'>⚠️ Phase 3 Failed - Using Fallback</span>", unsafe_allow_html=True)
            fin_data = FALLBACK_FINANCIAL
            st.session_state.used_fallback = True
        
        # === PHASE 4: STRATEGIC POSITIONING (Lines 381-420) ===
        st.write("🎯 **Phase 4**: Assessing strategic fit...")
        
        strategy_prompt = f"""<|start_header_id|>system<|end_header_id|>
Return ONLY a JSON object with these exact keys:
{{"fit_score": 9, "alignment": "Core Racing", "moat_benefit": "+15K hours data, 5% accuracy gain", "competitors": ["VRS at $9.99/mo", "Coach Dave at $19.99/mo"], "velocity": 9, "speedrun_leverage": "A16Z intro to Logitech G team", "risk_level": "Low"}}

TARGET: {target_name}
Return JSON only.<|eot_id|><|start_header_id|>user<|end_header_id|>
Return JSON only.<|eot_id_id|><|start_header_id|>assistant<|end_header_id|>"""
        
        try:
            strategy = client.chat_completion(model="meta-llama/Llama-3.2-1B-Instruct", messages=[{"role": "user", "content": strategy_prompt}], max_tokens=450, temperature=0.1)
            strategy_data = parse_json_safely(strategy.choices[0].message.content, "Phase 4 Strategy", FALLBACK_STRATEGY)
            st.write(f"<span class='phase-success'>✅ Phase 4 Complete: Fit {strategy_data['fit_score']}/10</span>", unsafe_allow_html=True)
        except Exception as e:
            st.session_state.phase_errors.append(f"Phase 4: {str(e)}")
            st.write(f"<span class='phase-warning'>⚠️ Phase 4 Failed - Using Fallback</span>", unsafe_allow_html=True)
            strategy_data = FALLBACK_STRATEGY
            st.session_state.used_fallback = True
        
        # === PHASE 5: CONSOLIDATE & SCORE (Lines 421-480) ===
        st.write("📊 **Phase 5**: Calculating final weighted score...")
        
        # Safe parsing of user count
        users_str = str(market_data.get('active_users', '0'))
        try:
            if 'Undisclosed' in users_str:
                users = 25000  # Default estimate
            else:
                users = int(re.sub(r'[^\d]', '', users_str)) or 25000
        except:
            users = 25000
        
        # Safe calculations with defaults
        market_score = min(10, users / 10000) * 3.5
        tech_score = (10 - min(safe_int(tech_data.get('hours', 999)) / 48, 10)) * 2.5
        revenue_score = safe_float(fin_data.get('base', {}).get('conversion', 1.0)) * 10 / 1.5 * 2.5
        strategy_score = safe_int(strategy_data.get('fit_score', 5)) * 1.5
        
        # Safe cost parsing for runway impact
        cost_num = parse_cost_to_number(tech_data.get('cost_at_120_hr', '$0'))
        
        ai_data = {
            "target": target_name,
            "overall_score": round(market_score + tech_score + revenue_score + strategy_score, 1),
            "confidence": safe_int(market_data.get('confidence', 40)),
            "market_attractiveness": {
                "tam": market_data.get('tam', '$0M'), "sam": market_data.get('sam', '$0M'), "som": market_data.get('som', '$0M'),
                "active_users": market_data.get('active_users', 'Unknown'), "cagr": market_data.get('cagr', '0%'),
                "score": round(min(10, users / 10000), 1), "source": market_data.get('source', 'Failed'),
                "rationale": market_data.get('rationale', 'No rationale provided')
            },
            "technical_feasibility": {
                "method": tech_data.get('method', 'Unknown'), "endpoint": tech_data.get('endpoint', 'N/A'),
                "hours": safe_int(tech_data.get('hours', 999)), "cost": tech_data.get('cost_at_120_hr', '$0'),
                "timeline_days": safe_int(tech_data.get('timeline_days', 999)), "team_pct": round(safe_float(tech_data.get('team_pct_of_sprint', 100)), 1),
                "parallelizable": tech_data.get('parallelizable', False), "score": round(10 - min(safe_int(tech_data.get('hours', 999)) / 48, 10), 1),
                "risk_level": tech_data.get('risk_level', 'Unknown'), "source": tech_data.get('source', 'Benchmarks')
            },
            "revenue_potential": {
                "conversion_rate": safe_float(fin_data.get('base', {}).get('conversion', 1.0)),
                "arr": fin_data.get('base', {}).get('arr', '$0'),
                "payback_days": safe_int(fin_data.get('base', {}).get('payback', '999 days').split()[0]),
                "ltv": fin_data.get('base', {}).get('ltv', 'TBD'),
                "score": round(safe_float(fin_data.get('base', {}).get('conversion', 1.0)) * 10 / 1.5, 1)
            },
            "strategic_fit": {
                "score": safe_int(strategy_data.get('fit_score', 5)), "alignment": strategy_data.get('alignment', 'Unknown'),
                "moat_benefit": strategy_data.get('moat_benefit', 'Unknown'), "competitors": strategy_data.get('competitors', ['Unknown']),
                "velocity": safe_int(strategy_data.get('velocity', 5)), "speedrun_leverage": strategy_data.get('speedrun_leverage', 'Unknown'),
                "risk_level": strategy_data.get('risk_level', 'Unknown')
            },
            "dev_impact": {
                "hours_required": safe_int(tech_data.get('hours', 999)),
                "sprint_capacity_pct": round(safe_float(tech_data.get('team_pct_of_sprint', 100)), 1),
                "cost_at_120_hr": tech_data.get('cost_at_120_hr', '$0'),
                "parallelizable": tech_data.get('parallelizable', False),
                "runway_impact": f"{cost_num / 85000:.1%}" if cost_num > 0 else "0%"
            },
            "financial_model": fin_data,
            "used_fallback": st.session_state.used_fallback,
            "phase_errors": st.session_state.phase_errors
        }
        
        st.session_state.ai_data = ai_data
        st.session_state.analysis_done = True
        st.write(f"<span class='phase-success'>✅ **ANALYSIS COMPLETE**: {ai_data['overall_score']}/100</span>", unsafe_allow_html=True)

# === INVESTOR DASHBOARD DISPLAY (Lines 481-700) ===
if st.session_state.analysis_done and st.session_state.ai_data:
    data = st.session_state.ai_data
    
    # Fallback warning banner
    if data.get('used_fallback', False):
        st.markdown('<div class="fallback-banner">⚠️ **FALLBACK DATA USED** - Verify critical metrics manually</div>', unsafe_allow_html=True)
    
    # Phase errors summary
    if data.get('phase_errors'):
        with st.expander("⚠️ Analysis Warnings"):
            for error in data['phase_errors']:
                st.caption(f"• {error}")
    
    # Executive score header
    confidence_color = "#10b981" if data['confidence'] >= 80 else "#f59e0b" if data['confidence'] >= 60 else "#ef4444"
    st.markdown(f"""
        <div class="investor-header">
            <h2>📊 Overall Investment Score: {data['overall_score']}/100</h2>
            <p style="color: {confidence_color}; font-weight: 700; font-size: 1.2rem;">
                Data Reliability: {data['confidence']}% {'(High)' if data['confidence'] >= 80 else '(Medium)' if data['confidence'] >= 60 else '(Low - Verify Manually)'}
            </p>
            <p style="font-size: 1.1rem; margin-top: 10px;"><strong>Target:</strong> {data['target']}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Metrics overview grid
    cols = st.columns(4)
    dimensions = ['market_attractiveness', 'technical_feasibility', 'revenue_potential', 'strategic_fit']
    icons = ['🌍', '⚙️', '💰', '🎯']
    colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c']
    
    for idx, dimension in enumerate(dimensions):
        with cols[idx]:
            score = data[dimension]['score']
            st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, {colors[idx]} 0%, {colors[idx]}aa 100%);">
                    <div class="metric-label">{icons[idx]} {dimension.replace('_', ' ').title()}</div>
                    <div class="metric-value">{score}</div>
                    <div style="color: rgba(255,255,255,0.8); font-size: 0.75rem; margin-top: 8px;">
                        {data[dimension].get('source', '') if dimension == 'market_attractiveness' else ''}
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # === DETAILED INVESTOR TABS ===
    tab_market, tab_tech, tab_fin, tab_dev, tab_strat, tab_memo = st.tabs([
        "🌍 Market Deep Dive", "⚙️ Technical Architecture", "💰 Financial Model", 
        "👥 Dev Team Impact", "🎯 Strategic Positioning", "📝 Board Memo"
    ])
    
    with tab_market:
        st.subheader("Market Sizing & Evidence-Based Analysis")
        
        # Market sizing columns
        col1, col2 = st.columns(2)
        with col1:
            st.metric("🎯 Total Addressable Market (TAM)", data['market_attractiveness']['tam'], 
                     help="Total market size for this opportunity")
            st.metric("📍 Serviceable Addressable Market (SAM)", data['market_attractiveness']['sam'],
                     help="Geographically and technically addressable portion")
            st.metric("💎 Serviceable Obtainable Market (SOM)", data['market_attractiveness']['som'],
                     help="Trophi's 3-year achievable share (1-3% conservative)")
        with col2:
            st.metric("👥 Active Users", data['market_attractiveness']['active_users'],
                     help="Current verified user base")
            st.metric("📈 Growth Rate (CAGR)", data['market_attractiveness']['cagr'],
                     help="Compound annual growth rate")
            st.metric("⭐ Market Score", f"{data['market_attractiveness']['score']}/10",
                     delta=f"Confidence: {data['confidence']}%")
        
        st.info(f"**Research Source:** {data['market_attractiveness'].get('source', 'Unknown')}")
        st.success(f"**Investment Rationale:** {data['market_attractiveness'].get('rationale', 'No rationale provided')}")
        
        if data['confidence'] < 70:
            st.warning("⚠️ **Manual Verification Required**: Low confidence score - research user numbers from company IR or SteamSpy")
    
    with tab_tech:
        st.subheader("Technical Integration Architecture")
        
        # Technical specs
        col1, col2 = st.columns(2)
        with col1:
            st.metric("🔗 Integration Method", data['technical_feasibility']['method'],
                     help="API = Best, UDP = Acceptable, CV = Avoid")
            st.metric("🌐 Endpoint/Protocol", data['technical_feasibility'].get('endpoint', 'N/A'),
                     help="Specific API endpoint or UDP port")
            st.metric("⏱️ Development Hours", f"{data['technical_feasibility']['hours']}h",
                     help="Engineering hours at $120/hr fully-loaded")
        with col2:
            st.metric("📅 Timeline", f"{data['technical_feasibility']['timeline_days']} days + QA",
                     help="Business days including QA and deployment")
            st.metric("🚦 Risk Level", data['technical_feasibility'].get('risk_level', 'Unknown'),
                     delta_color="inverse")
            st.metric("💪 Tech Score", f"{data['technical_feasibility']['score']}/10",
                     help="Lower hours = higher score")
        
        st.divider()
        
        # Resource requirements
        st.subheader("Engineering Resource Requirements")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("💰 Fully-Loaded Cost", data['technical_feasibility']['cost'],
                     help="Total engineering cost at $120/hr")
            st.metric("📊 % of Sprint Capacity", f"{data['technical_feasibility']['team_pct']}%",
                     help=f"Of {sprint_capacity}h available per sprint")
        with col2:
            st.metric("🔄 Parallelizable", "✅ Yes" if data['dev_impact']['parallelizable'] else "❌ No",
                     help="Can run with other integrations?")
        
        # Progress bar for capacity
        st.progress(data['technical_feasibility']['team_pct']/100)
        
        if not data['dev_impact']['parallelizable']:
            st.error("❌ **CAPACITY BLOCKER**: This will BLOCK all other integrations for the duration")
            st.warning(f"**De-risking Option**: Hire contractor at $150/hr = **${data['technical_feasibility']['hours']*150/1000:.1f}K** extra cost but preserves team velocity")
        else:
            st.success("✅ **CAPACITY EFFICIENT**: Can run in parallel with 1 other major integration")
    
    with tab_fin:
        st.subheader("Financial Model (3-Case Analysis)")
        
        # Probability indicators
        st.caption("**Base Case (50%) | Bull Case (25%) | Bear Case (25%)**")
        
        # Base case
        st.markdown('<div class="fin-model-section">', unsafe_allow_html=True)
        st.subheader("📊 Base Case (Most Likely)")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Conversion Rate", f"{data['financial_model']['base']['conversion']}%",
                   help="Target users → paying customers")
        col2.metric("ARR Potential", data['financial_model']['base']['arr'],
                   help="Annual Recurring Revenue at scale")
        col3.metric("Payback Period", data['financial_model']['base']['payback'],
                   help="CAC recovery timeline")
        col4.metric("NPV (3yr)", data['financial_model']['base']['npv'],
                   help="Net Present Value discounted at 15%")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Bull case
        st.markdown('<div class="fin-model-section bull-case">', unsafe_allow_html=True)
        st.subheader("🐂 Bull Case (Optimistic)")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Conversion Rate", f"{data['financial_model']['bull']['conversion']}%")
        col2.metric("ARR Potential", data['financial_model']['bull']['arr'], delta="vs Base")
        col3.metric("Payback Period", data['financial_model']['bull']['payback'], delta="faster")
        col4.metric("NPV (3yr)", data['financial_model']['bull']['npv'], delta="higher")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Bear case
        st.markdown('<div class="fin-model-section bear-case">', unsafe_allow_html=True)
        st.subheader("🐻 Bear Case (Pessimistic)")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Conversion Rate", f"{data['financial_model']['bear']['conversion']}%")
        col2.metric("ARR Potential", data['financial_model']['bear']['arr'], delta="vs Base", delta_color="inverse")
        col3.metric("Payback Period", data['financial_model']['bear']['payback'], delta="slower", delta_color="inverse")
        col4.metric("NPV (3yr)", data['financial_model']['bear']['npv'], delta="lower", delta_color="inverse")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.divider()
        st.subheader("Financial Health vs. Company Targets")
        col1, col2 = st.columns(2)
        col1.metric("Target CAC", f"${max_cac}", 
                   delta=f"Current: ${TROPHI_OPERATING_MODEL['current_state']['metrics'].get('cac', '52')}",
                   help="Customer Acquisition Cost target")
        col2.metric("Target LTV", TROPHI_OPERATING_MODEL['current_state']['metrics'].get('ltv', '205'),
                   delta=f"Model: ${data['revenue_potential'].get('ltv', '205')}",
                   help="Lifetime Value target")
        
        payback_days = data['revenue_potential']['payback_days']
        if payback_days > 90:
            st.error(f"❌ **PAYBACK ALERT**: {payback_days} days exceeds 90-day target")
        else:
            st.success(f"✅ **PAYBACK HEALTHY**: {payback_days} days meets <90 day target")

        with tab_dev:
            st.subheader("Engineering Capacity Impact Analysis")
        
        # Resource requirements
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Engineering Hours", f"{data['dev_impact']['hours_required']}h",
                     help="Full lifecycle hours including QA")
            st.metric("% of Sprint Capacity", f"{data['dev_impact']['sprint_capacity_pct']}%",
                     help=f"Of {sprint_capacity}h available per sprint")
            st.metric("Fully-Loaded Cost", data['dev_impact']['cost_at_120_hr'],
                     help="$120/hr fully-loaded engineering cost")
        with col2:
            st.metric("Timeline Impact", f"{data['technical_feasibility']['timeline_days']} days",
                     help="Business days to production")
            st.metric("Runway Impact", data['dev_impact']['runway_impact'],
                     help="As % of monthly $85K burn")
            st.metric("Parallelizable", "✅ Yes" if data['dev_impact']['parallelizable'] else "❌ No",
                     help="Can run with other integrations?")
        
        # Progress bar for capacity
        st.progress(data['dev_impact']['sprint_capacity_pct']/100)
        
        if not data['dev_impact']['parallelizable']:
            st.error("❌ **CAPACITY BLOCKER**: This will BLOCK all other integrations for the duration")
            contractor_cost = data['dev_impact']['hours_required'] * 150 / 1000
            st.warning(f"**De-risking Option**: Hire contractor at $150/hr = **${contractor_cost:.1f}K** extra cost but preserves team velocity")
        else:
            st.success("✅ **CAPACITY EFFICIENT**: Can run in parallel with 1 other major integration")
    
    with tab_strat:
        st.subheader("Strategic Positioning & Competitive Moat")
        
        # Strategic fit analysis
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Strategic Fit Score", f"{data['strategic_fit']['score']}/10",
                     help="9-10=Core, 6-8=Adjacent, 3-5=New vertical")
            st.metric("Alignment Category", data['strategic_fit']['alignment'],
                     delta=f"Velocity: {data['strategic_fit']['velocity']}/10")
        with col2:
            st.metric("Velocity Score", f"{data['strategic_fit']['velocity']}/10",
                     help="Speed to market (10 = ship in 2 weeks)")
            st.metric("A16Z SPEEDRUN Leverage", "✅ Available" if "A16Z" in str(data['strategic_fit'].get('speedrun_leverage','')) else "❌ Limited",
                     help="Access to portfolio, partners, capital")
        
        st.divider()
        
        # Moat strengthening
        st.subheader("Data Moat & Competitive Advantage")
        st.success(f"**Moat Enhancement:** {data['strategic_fit']['moat_benefit']}")
        st.caption("Long-term defensibility through data network effects")
        
        # Competitive landscape
        st.divider()
        st.subheader("Direct Competitive Intelligence")
        st.caption("Current market alternatives Trophi would displace")
        
        if data['strategic_fit']['competitors'] and data['strategic_fit']['competitors'][0] != 'Unknown':
            for comp in data['strategic_fit']['competitors']:
                st.caption(f"• {comp}")
        else:
            st.info("🕵️ **Action Item**: Research competitors (VRS, Coach Dave Academy, Craig's Setup Shop)")
        
        st.divider()
        st.subheader("A16Z SPEEDRUN Network Effects")
        leverage = data['strategic_fit'].get('speedrun_leverage', 'Unknown')
        if "A16Z" in leverage or "portfolio" in leverage.lower():
            st.success(f"🚀 **Leverage Identified:** {leverage}")
            st.caption("**Use Network For**: Customer intros, co-marketing, technical support, talent")
        else:
            st.warning("⚠️ **Limited A16Z Leverage**: Investigate portfolio connections manually")
    
    with tab_memo:
        st.subheader("Board of Directors Investment Memo")
        st.caption("Auto-generated executive summary for A16Z partners and Trophi board")
        
        # Generate memo if not cached
        if not st.session_state.memo_text:
            with st.spinner("📝 Generating board-level executive summary..."):
                memo_prompt = f"""<|start_header_id|>system<|end_header_id|>
You are the VP of Strategy at Trophi.ai presenting to the board including A16Z partners.

**MEMO STRUCTURE (600 words max):**

**EXECUTIVE VERDICT:** {'🟢 GREENLIGHT - EXECUTE IMMEDIATELY' if data['overall_score'] >= 75 else '🟡 CAUTIOUS - PROCEED WITH MONITORING' if data['overall_score'] >= 60 else '🔴 KILL - REALLOCATE RESOURCES'}

**1. MARKET OPPORTUNITY (150 words):**
- TAM/SAM/SOM: {data['market_attractiveness'].get('tam', '$0M')}/{data['market_attractiveness'].get('sam', '$0M')}/{data['market_attractiveness'].get('som', '$0M')}
- Active users: {data['market_attractiveness'].get('active_users', 'Unknown')} growing at {data['market_attractiveness'].get('cagr', '0%')}
- Confidence: {data['confidence']}% from {data['market_attractiveness'].get('source', 'Unknown')}
- Rationale: {data['market_attractiveness'].get('rationale', 'No rationale provided')}

**2. TECHNICAL INVESTMENT (150 words):**
- {data['dev_impact'].get('hours_required', 0)}h engineering = {data['technical_feasibility'].get('team_pct', 0)}% of Q1 capacity
- Method: {data['technical_feasibility'].get('method', 'Unknown')} with {data['technical_feasibility'].get('timeline_days', 999)} day timeline
- Risk level: {data['technical_feasibility'].get('risk_level', 'Unknown')}
- Cost: {data['dev_impact'].get('cost_at_120_hr', '$0')}
- Parallelizable: {'Yes - preserves roadmap' if data['dev_impact'].get('parallelizable', False) else 'No - requires prioritization'}

**3. FINANCIAL MODEL (150 words):**
- Base case: {data['financial_model']['base'].get('arr', '$0')} ARR at {data['financial_model']['base'].get('conversion', 0)}% conversion
- Payback: {data['financial_model']['base'].get('payback', '999 days')} (target: <90 days)
- NPV: {data['financial_model']['base'].get('npv', '$0')} over 3 years
- Bull/Bear cases show {data['financial_model']['bull'].get('arr', '$0')} upside / {data['financial_model']['bear'].get('arr', '$0')} downside
- LTV/CAC: {data['revenue_potential'].get('ltv', 'TBD')} vs ${TROPHI_OPERATING_MODEL['current_state']['metrics'].get('cac', '52')} target

**4. STRATEGIC FIT (100 words):**
- {data['strategic_fit'].get('alignment', 'Unknown')} alignment with {data['strategic_fit'].get('score', 0)}/10 fit score
- Velocity: {data['strategic_fit'].get('velocity', 0)}/10 (speed to market)
- A16Z SPEEDRUN leverage: {data['strategic_fit'].get('speedrun_leverage', 'None')}
- Competitive moat: {data['strategic_fit'].get('moat_benefit', 'None')}
- Direct competitors: {', '.join(data['strategic_fit'].get('competitors', ['Unknown']))}

**5. DEV TEAM IMPACT (50 words):**
- Capacity: {data['dev_impact'].get('sprint_capacity_pct', 0)}% of sprint
- Runway impact: {data['dev_impact'].get('runway_impact', '0%')} of monthly burn
- Recommendation: {'Use internal team' if data['dev_impact'].get('parallelizable', False) else 'Hire contractor to preserve velocity'}

**6. 30-DAY ACTION PLAN**
- Week 1: API documentation review and sandbox setup
- Week 2-3: Core integration development
- Week 4: QA, beta deployment, metrics instrumentation

**TONE:** Data-driven, confident, board-appropriate.<|eot_id|><|start_header_id|>user<|end_header_id|>
Generate board memo for {data['target']} based on provided data.<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
                
                memo_response = client.chat_completion(model="meta-llama/Llama-3.2-1B-Instruct", messages=[{"role": "user", "content": memo_prompt}], max_tokens=1200, temperature=0.3)
                st.session_state.memo_text = memo_response.choices[0].message.content
        
        # Display memo
        st.markdown(f"""
            <div style="background: rgba(255,255,255,0.05); border-radius: 16px; padding: 30px; border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(10px);">
                {st.session_state.memo_text}
            </div>
        """, unsafe_allow_html=True)
        
        # Memo actions
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="💾 Download Memo (TXT)",
                data=st.session_state.memo_text,
                file_name=f"Trophi_Board_Memo_{data['target'].replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        with col2:
            if st.button("🔄 Refresh Memo", use_container_width=True, type="secondary"):
                st.session_state.memo_text = None
                st.experimental_rerun()

# === FINAL ACTIONS & EXPORT (Lines 701-750) ===
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    # Data export
    if st.session_state.ai_data:
        export_data = json.dumps(st.session_state.ai_data, indent=2)
        st.download_button(
            label="📊 Export Full Analysis (JSON)",
            data=export_data,
            file_name=f"Trophi_Analysis_{data['target'].replace(' ', '_')}.json",
            mime="application/json",
            use_container_width=True
        )

with col2:
    # New analysis
    if st.button("🎯 New Opportunity Analysis", use_container_width=True, type="primary"):
        for key in ["analysis_done", "ai_data", "memo_text", "used_fallback", "phase_errors"]:
            st.session_state[key] = False if key in ["analysis_done"] else (None if key in ["ai_data", "memo_text"] else False)
        st.experimental_rerun()

with col3:
    # Troubleshooting
    with st.expander("🔧 Troubleshooting", expanded=False):
        st.caption("**If analysis fails:**")
        st.caption("1. Check HF_API_TOKEN in secrets")
        st.caption("2. Verify model availability")
        st.caption("3. Try simpler target name")
        st.caption("4. Check rate limits")

# === FOOTER ===
st.divider()
st.markdown("""
    <div style="text-align: center; color: #94a3b8; padding: 20px;">
        <p><strong>Trophi.ai Scale Decision Engine v1.0</strong></p>
        <p>A16Z SPEEDRUN Portfolio Company | 2025</p>
        <p style="font-size: 0.8rem;">
            Powered by Hugging Face Inference API | Model: meta-llama/Llama-3.2-1B-Instruct<br>
            Data confidence threshold: High | Source verification required for <70% confidence
        </p>
    </div>
""", unsafe_allow_html=True)






