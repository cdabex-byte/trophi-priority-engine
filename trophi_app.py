import streamlit as st
import json
import re
from huggingface_hub import InferenceClient

# === SAFE STRING PARSING UTILS ===
def parse_cost_to_number(cost_str):
    """Convert '$4,800' or '$14.4K' to integer cents"""
    try:
        # Remove $ and commas
        clean = str(cost_str).replace('$', '').replace(',', '')
        # Handle K suffix
        if 'K' in clean:
            return int(float(clean.replace('K', '')) * 1000)
        elif 'M' in clean:
            return int(float(clean.replace('M', '')) * 1000000)
        return int(float(clean))
    except:
        return 0  # Safe default

def safe_int(value, default=0):
    """Safely convert any value to int"""
    try:
        if isinstance(value, str):
            # Remove commas and non-numeric chars
            cleaned = re.sub(r'[^\d]', '', value)
            return int(cleaned) if cleaned else default
        return int(value)
    except:
        return default

def safe_float(value, default=0.0):
    """Safely convert any value to float"""
    try:
        return float(value)
    except:
        return default

# === ENHANCED JSON PARSER ===
def parse_json_safely(text, phase_name="Parse", fallback_data=None):
    """
    Ultra-robust JSON extraction with automatic repair
    """
    try:
        # Debug: Show raw response
        debug_len = min(len(text), 500)
        st.write(f"🔍 Debug ({phase_name}): First {debug_len} chars: `{text[:debug_len]}...`")
        
        # Aggressive cleaning
        text = re.sub(r'```json|```', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\[.*?\]', '', text)  # Remove markdown links
        text = re.sub(r'\*\*.*?\*\*', '', text)  # Remove bold
        text = re.sub(r'//.*?\n', '', text)  # Remove comments
        
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
        elif close_braces > open_braces:
            json_str = '{' * (close_braces - open_braces) + json_str
        
        # Parse
        result = json.loads(json_str)
        
        # Validate against fallback
        if fallback_data:
            for key, default_value in fallback_data.items():
                if key not in result:
                    st.warning(f"⚠️ Missing '{key}' in {phase_name}, using fallback: {default_value}")
                    result[key] = default_value
        
        return result
        
    except Exception as e:
        st.error(f"❌ **{phase_name} Failed**: {str(e)}")
        
        with st.expander(f"🐛 Debug: Full {phase_name} Response"):
            st.code(text, language="text")
        
        if fallback_data:
            st.info(f"✅ Using fallback data for {phase_name}")
            return fallback_data
        
        # Empty structure fallback
        return {
            "tam": "$0M", "sam": "$0M", "som": "$0M",
            "active_users": "Unknown", "source": "Failed to parse",
            "cagr": "0%", "confidence": 0,
            "method": "Unknown", "hours": 999, "cost_at_120_hr": "$0",
            "timeline_days": 999, "team_pct_of_sprint": 100,
            "parallelizable": False,
            "base": {"conversion": 0, "arr": "$0", "payback": "999 days", "npv": "$0"},
            "bull": {"conversion": 0, "arr": "$0", "payback": "999 days", "npv": "$0"},
            "bear": {"conversion": 0, "arr": "$0", "payback": "999 days", "npv": "$0"},
            "fit_score": 0, "alignment": "Unknown", "moat_benefit": "None",
            "competitors": ["Parse failed"], "velocity": 0, "speedrun_leverage": "None"
        }

# === ENTERPRISE MODEL ===
TROPHI_OPERATING_MODEL = {
    "current_state": {
        "team": {"total": 22, "engineering": 8, "burn_rate": "$85K/month", "runway": "38 months"},
        "metrics": {"ltv": "$205", "cac": "$52", "mrr": "$47K"}
    }
}

# === COMPREHENSIVE FALLBACK DATA ===
FALLBACK_MARKET = {
    "tam": "$25M", "sam": "$12M", "som": "$1.2M",
    "active_users": "Undisclosed (est. 15K from similar titles)", 
    "source": "Industry estimation - REQUIRES MANUAL VERIFICATION",
    "cagr": "5-10% (conservative)", 
    "confidence": 35
}

FALLBACK_TECH = {
    "method": "UDP (assume telemetry)",
    "endpoint": "Standard port (research needed)",
    "hours": 120, 
    "cost_at_120_hr": "$14,400",
    "timeline_days": 14, 
    "qa_days": 5,
    "team_pct_of_sprint": 37.5,
    "parallelizable": False
}

FALLBACK_FINANCIAL = {
    "base": {"conversion": 1.0, "arr": "$180K", "payback": "120 days", "npv": "$0.4M"},
    "bull": {"conversion": 2.0, "arr": "$360K", "payback": "75 days", "npv": "$0.9M"},
    "bear": {"conversion": 0.5, "arr": "$90K", "payback": "180 days", "npv": "$0.1M"}
}

FALLBACK_STRATEGY = {
    "fit_score": 5, 
    "alignment": "Unknown (requires product review)", 
    "moat_benefit": "Limited information available",
    "competitors": ["Manual research required"], 
    "velocity": 5, 
    "speedrun_leverage": "Investigate A16Z network"
}

# === UI STYLING ===
st.markdown("""
    <style>
    .investor-header { background: rgba(15, 23, 42, 0.8); backdrop-filter: blur(20px); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 20px; padding: 40px; margin-bottom: 30px; }
    .metric-card { background: linear-gradient(135deg, rgba(99, 102, 241, 0.9) 0%, rgba(124, 58, 237, 0.9) 100%); border-radius: 16px; padding: 25px; border: 1px solid rgba(255, 255, 255, 0.1); }
    .metric-value { font-weight: 900; font-size: 3rem; color: white; }
    .metric-label { color: rgba(255, 255, 255, 0.8); font-weight: 600; font-size: 0.85rem; text-transform: uppercase; }
    .fallback-banner { background: rgba(245, 158, 11, 0.2); border: 2px solid #f59e0b; border-radius: 12px; padding: 15px; margin: 15px 0; font-weight: 600; }
    .phase-success { color: #10b981; }
    .phase-warning { color: #f59e0b; }
    .phase-error { color: #ef4444; }
    </style>
""", unsafe_allow_html=True)

# === SESSION STATE ===
for key in ["analysis_done", "ai_data", "memo_text", "used_fallback", "phase_errors"]:
    if key not in st.session_state:
        st.session_state[key] = False if key == "analysis_done" else (None if key in ["ai_data", "memo_text"] else False)

# === INPUT ===
st.markdown('<div class="investor-header">', unsafe_allow_html=True)
st.title("🧠 Trophi.ai Scale Decision Engine")
st.caption("**Investor-Grade Opportunity Assessment** | A16Z SPEEDRUN Portfolio")
st.markdown('</div>', unsafe_allow_html=True)

col_input, col_btn = st.columns([4, 1])
with col_input:
    target_name = st.text_input("", placeholder="Enter opportunity...")
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
        
        # === PHASE 1: MARKET INTELLIGENCE ===
        st.write("📡 **Phase 1**: Gathering verifiable market data...")
        
        market_prompt = f"""<|start_header_id|>system<|end_header_id|>
Return ONLY a JSON object with these exact keys:
{{"tam": "$XM", "sam": "$XM", "som": "$XM", "active_users": "X,XXX", "source": "SteamSpy", "cagr": "X%", "confidence": 80}}

RULES:
- No markdown
- No explanations
- No extra text
- If unknown, use "Undisclosed (est. 10K)" and confidence: 40

TARGET: {target_name}<|eot_id|><|start_header_id|>user<|end_header_id|>
Return JSON only.<|eot_id_id|><|start_header_id|>assistant<|end_header_id|>"""
        
        try:
            market = client.chat_completion(model="meta-llama/Llama-3.2-1B-Instruct", messages=[{"role": "user", "content": market_prompt}], max_tokens=400, temperature=0.1)
            market_data = parse_json_safely(market.choices[0].message.content, "Phase 1 Market", FALLBACK_MARKET)
            st.write(f"<span class='phase-success'>✅ Phase 1 Complete: {market_data['confidence']}% confidence</span>", unsafe_allow_html=True)
        except Exception as e:
            st.session_state.phase_errors.append(f"Phase 1: {e}")
            st.write(f"<span class='phase-warning'>⚠️ Phase 1 Failed - Using Fallback</span>", unsafe_allow_html=True)
            market_data = FALLBACK_MARKET
            st.session_state.used_fallback = True
        
        # === PHASE 2: TECHNICAL ARCHITECTURE ===
        st.write("⚙️ **Phase 2**: Mapping integration architecture...")
        
        tech_prompt = f"""<|start_header_id|>system<|end_header_id|>
Return ONLY a JSON object:
{{"method": "API|UDP", "endpoint": "URL|Port", "hours": 40, "cost_at_120_hr": "$4,800", "timeline_days": 5, "team_pct_of_sprint": 12.5, "parallelizable": true}}

TARGET: {target_name}<|eot_id|><|start_header_id|>user<|end_header_id|>
Return JSON only.<|eot_id_id|><|start_header_id|>assistant<|end_header_id|>"""
        
        try:
            tech = client.chat_completion(model="meta-llama/Llama-3.2-1B-Instruct", messages=[{"role": "user", "content": tech_prompt}], max_tokens=450, temperature=0.1)
            tech_data = parse_json_safely(tech.choices[0].message.content, "Phase 2 Tech", FALLBACK_TECH)
            st.write(f"<span class='phase-success'>✅ Phase 2 Complete: {tech_data['hours']}h</span>", unsafe_allow_html=True)
        except Exception as e:
            st.session_state.phase_errors.append(f"Phase 2: {e}")
            st.write(f"<span class='phase-warning'>⚠️ Phase 2 Failed - Using Fallback</span>", unsafe_allow_html=True)
            tech_data = FALLBACK_TECH
            st.session_state.used_fallback = True
        
        # === PHASE 3: FINANCIAL MODEL ===
        st.write("💰 **Phase 3**: Building 3-case P&L...")
        
        fin_prompt = f"""<|start_header_id|>system<|end_header_id|>
Return ONLY a JSON object:
{{"base": {{"conversion": 1.5, "arr": "$420K", "payback": "94 days", "npv": "$1.2M"}}, "bull": {{"conversion": 2.5, "arr": "$700K", "payback": "63 days", "npv": "$2.1M"}}, "bear": {{"conversion": 0.8, "arr": "$224K", "payback": "157 days", "npv": "$0.4M"}}}}<|eot_id|><|start_header_id|>user<|end_header_id|>
Users: {market_data['active_users']}
Return JSON only.<|eot_id_id|><|start_header_id|>assistant<|end_header_id|>"""
        
        try:
            fin = client.chat_completion(model="meta-llama/Llama-3.2-1B-Instruct", messages=[{"role": "user", "content": fin_prompt}], max_tokens=600, temperature=0.1)
            fin_data = parse_json_safely(fin.choices[0].message.content, "Phase 3 Financial", FALLBACK_FINANCIAL)
            st.write(f"<span class='phase-success'>✅ Phase 3 Complete: {fin_data['base']['arr']} base case</span>", unsafe_allow_html=True)
        except Exception as e:
            st.session_state.phase_errors.append(f"Phase 3: {e}")
            st.write(f"<span class='phase-warning'>⚠️ Phase 3 Failed - Using Fallback</span>", unsafe_allow_html=True)
            fin_data = FALLBACK_FINANCIAL
            st.session_state.used_fallback = True
        
        # === PHASE 4: STRATEGIC POSITIONING ===
        st.write("🎯 **Phase 4**: Assessing strategic fit...")
        
        strategy_prompt = f"""<|start_header_id|>system<|end_header_id|>
Return ONLY a JSON object:
{{"fit_score": 9, "alignment": "Core Racing", "moat_benefit": "15K hours data", "competitors": ["VRS at $9.99"], "velocity": 9, "speedrun_leverage": "A16Z intro to Fanatec"}}<|eot_id|><|start_header_id|>user<|end_header_id|>
Target: {target_name}
Return JSON only.<|eot_id_id|><|start_header_id|>assistant<|end_header_id|>"""
        
        try:
            strategy = client.chat_completion(model="meta-llama/Llama-3.2-1B-Instruct", messages=[{"role": "user", "content": strategy_prompt}], max_tokens=450, temperature=0.1)
            strategy_data = parse_json_safely(strategy.choices[0].message.content, "Phase 4 Strategy", FALLBACK_STRATEGY)
            st.write(f"<span class='phase-success'>✅ Phase 4 Complete: Fit {strategy_data['fit_score']}/10</span>", unsafe_allow_html=True)
        except Exception as e:
            st.session_state.phase_errors.append(f"Phase 4: {e}")
            st.write(f"<span class='phase-warning'>⚠️ Phase 4 Failed - Using Fallback</span>", unsafe_allow_html=True)
            strategy_data = FALLBACK_STRATEGY
            st.session_state.used_fallback = True
        
        # === PHASE 5: CONSOLIDATE ===
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
        
        # Safe calculations with .get() and defaults
        market_score = min(10, users / 10000) * 3.5
        tech_score = (10 - min(safe_int(tech_data.get('hours', 999)) / 48, 10)) * 2.5
        revenue_score = safe_float(fin_data.get('base', {}).get('conversion', 1.0)) * 10 / 1.5 * 2.5
        strategy_score = safe_int(strategy_data.get('fit_score', 5)) * 1.5
        
        # Safe cost parsing for runway impact
        cost_str = str(tech_data.get('cost_at_120_hr', '$0'))
        cost_num = parse_cost_to_number(cost_str)
        
        ai_data = {
            "target": target_name,
            "overall_score": round(market_score + tech_score + revenue_score + strategy_score, 1),
            "confidence": safe_int(market_data.get('confidence', 40)),
            "market_attractiveness": {
                "tam": market_data.get('tam', '$0M'), "sam": market_data.get('sam', '$0M'), "som": market_data.get('som', '$0M'),
                "active_users": market_data.get('active_users', 'Unknown'), "cagr": market_data.get('cagr', '0%'),
                "score": round(min(10, users / 10000), 1), "source": market_data.get('source', 'Unknown')
            },
            "technical_feasibility": {
                "method": tech_data.get('method', 'Unknown'), "endpoint": tech_data.get('endpoint', 'N/A'),
                "hours": safe_int(tech_data.get('hours', 999)), "cost": tech_data.get('cost_at_120_hr', '$0'),
                "timeline_days": safe_int(tech_data.get('timeline_days', 999)), "team_pct": round(safe_float(tech_data.get('team_pct_of_sprint', 100)), 1),
                "parallelizable": tech_data.get('parallelizable', False), "score": round(10 - min(safe_int(tech_data.get('hours', 999)) / 48, 10), 1)
            },
            "revenue_potential": {
                "conversion_rate": safe_float(fin_data.get('base', {}).get('conversion', 1.0)),
                "arr": fin_data.get('base', {}).get('arr', '$0'),
                "payback_days": safe_int(fin_data.get('base', {}).get('payback', '999 days').split()[0]),
                "score": round(safe_float(fin_data.get('base', {}).get('conversion', 1.0)) * 10 / 1.5, 1)
            },
            "strategic_fit": {
                "score": safe_int(strategy_data.get('fit_score', 5)),
                "alignment": strategy_data.get('alignment', 'Unknown'),
                "moat_benefit": strategy_data.get('moat_benefit', 'Unknown'),
                "competitors": strategy_data.get('competitors', ['Unknown']),
                "velocity": safe_int(strategy_data.get('velocity', 5)),
                "speedrun_leverage": strategy_data.get('speedrun_leverage', 'Unknown')
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
        st.write(f"<span class='phase-success'>✅ Analysis Complete: {ai_data['overall_score']}/100</span>", unsafe_allow_html=True)

# === DISPLAY RESULTS ===
if st.session_state.analysis_done and st.session_state.ai_data:
    data = st.session_state.ai_data
    
    # Show fallback warning banner
    if data.get('used_fallback', False):
        st.markdown('<div class="fallback-banner">⚠️ **THIS ANALYSIS USED FALLBACK DATA** - Manual verification required before decision</div>', unsafe_allow_html=True)
    
    # Show phase errors if any
    if data.get('phase_errors'):
        with st.expander("⚠️ Analysis Warnings"):
            for error in data['phase_errors']:
                st.caption(f"• {error}")
    
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
    
    # Rest of display logic remains the same...
    # (Full display code with safe access would go here)
    
    # CRITICAL: Add retry button for API failures
    if data.get('used_fallback'):
        st.divider()
        if st.button("🔄 Retry Analysis with Different Prompt", type="secondary"):
            st.session_state.analysis_done = False
            st.experimental_rerun()

# === FOOTER ===
st.divider()
st.caption("📊 **Trophi.ai Scale Engine** | A16Z SPEEDRUN | Fallback mode enabled for reliability")
