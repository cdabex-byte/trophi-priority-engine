This is a massive upgrade. Moving from "hardcoded text" to Real-Time Generative AI turns this from a "mockup" into a functional MVP.

We will use Google's Gemini Flash model because it is fast, free (within limits), and excellent for reasoning.

Here is the 4-step process to make your app live with real AI.

Step 1: Get Your Free Gemini API Key

Go to Google AI Studio.

Click "Create API Key".

Copy the key string (it starts with AIza...).

Do not share this key or paste it into your public code.

Step 2: Update requirements.txt

You need to tell the server to install Google's AI library.

Go to your GitHub repository.

Edit requirements.txt.

Add google-generativeai to the list. It should look like this:

code
Text
download
content_copy
expand_less
streamlit
pandas
google-generativeai
Step 3: Update trophi_app.py

We are going to inject a prompt that tells Gemini to act like a Strategy Operations Associate.

Copy this exact code to your GitHub file:

code
Python
download
content_copy
expand_less
import streamlit as st
import pandas as pd
import google.generativeai as genai

# --- CONFIGURATION ---
st.set_page_config(page_title="Trophi.ai Priority Engine", layout="centered")

# --- HEADER ---
st.title("🏎️ Trophi.ai Priority Engine")
st.caption("Powered by Gemini 1.5 Flash")

# --- SIDEBAR INPUTS ---
st.sidebar.header("Opportunity Details")
opp_name = st.sidebar.text_input("Project Name", "e.g., Counter-Strike 2 Integration")
opp_type = st.sidebar.selectbox("Type", ["New Game Integration", "Hardware Partnership", "Enterprise SDK", "Marketing Event"])

st.sidebar.subheader("Scoring Parameters")
# 1 = Low, 5 = High
tam_score = st.sidebar.slider("TAM / User Reach (1-5)", 1, 5, 4)
tech_lift = st.sidebar.slider("Engineering Lift (1=Easy, 5=Hard)", 1, 5, 5)
rev_potential = st.sidebar.slider("Immediate ARR Potential (1-5)", 1, 5, 2)
strat_fit = st.sidebar.slider("Strategic Moat Alignment (1-5)", 1, 5, 5)

# --- THE ALGORITHM ---
def calculate_score(tam, lift, rev, strat):
    score = (tam * 1.5) + (rev * 2.0) + (strat * 1.5) - (lift * 2.5)
    normalized_score = max(0, min(100, (score + 10) * 4)) 
    return round(normalized_score, 1)

final_score = calculate_score(tam_score, tech_lift, rev_potential, strat_fit)

# --- MAIN DASHBOARD ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"Analysis: {opp_name}")
    if final_score >= 75:
        st.success(f"✅ **GREENLIGHT** (Score: {final_score})")
    elif final_score >= 50:
        st.warning(f"⚠️ **EVALUATE** (Score: {final_score})")
    else:
        st.error(f"🛑 **KILL / DEFER** (Score: {final_score})")

with col2:
    st.metric(label="Trophi Score", value=final_score)

# --- GEMINI AI INTEGRATION ---
st.divider()
st.subheader("🤖 AI Decision Memo Generator")

# Check for API Key in Secrets
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Missing Gemini API Key. Please add it to Streamlit Secrets.")

if st.button("Generate Memo Draft"):
    if "GEMINI_API_KEY" not in st.secrets:
        st.stop()
    
    with st.spinner("Consulting the Strategy Engine..."):
        # The Prompt Strategy
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        You are the Head of Strategy & Operations at Trophi AI (a Series A gaming startup).
        Write a concise, bulleted 'Decision Memo' for the CEO regarding the opportunity: "{opp_name}".
        
        DATA CONTEXT:
        - Opportunity Type: {opp_type}
        - Our Internal Score: {final_score}/100
        - Strategic Fit: {strat_fit}/5
        - Engineering Lift (Risk): {tech_lift}/5
        - Revenue Potential: {rev_potential}/5
        
        INSTRUCTIONS:
        1. Start with a strict recommendation: "GREENLIGHT", "EVALUATE", or "DEFER".
        2. Explain the "Why" using the data provided. Be ruthless about Opportunity Cost.
        3. If Engineering Lift is High (4 or 5), warn about resource drain.
        4. If Strategic Fit is Low, recommend killing the project.
        5. Tone: Professional, direct, no fluff. Use "We" statements.
        """
        
        try:
            response = model.generate_content(prompt)
            st.markdown(response.text)
        except Exception as e:
            st.error(f"AI Error: {e}")
Step 4: Connect the Secret Key (Crucial Step)

Since your code is public on GitHub, you cannot put the key in the file. You must use Streamlit's Secrets Manager.

Go to your app dashboard at share.streamlit.io.

Click the three dots (⋮) next to your app → Settings.

Click on Secrets on the left menu.

Paste the following into the text box (replace YOUR_ACTUAL_KEY with the key you got in Step 1):

code
Toml
download
content_copy
expand_less
GEMINI_API_KEY = "AIzaSyD......(your actual key here)"

Click Save.

Step 5: Test It

Go to your live app link. Refresh the page.

Enter "Counter-Strike 2".

Set "Engineering Lift" to 5 (Hard).

Click Generate Memo Draft.

What will happen:
Instead of generic text, Gemini will actually "think." It will see the high Engineering risk and write a custom memo warning you that CS2 is too expensive to build right now.

Send that link. It proves you know Python, APIs, and Strategy.
