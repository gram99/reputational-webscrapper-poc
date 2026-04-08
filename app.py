import streamlit as st
import pandas as pd
import requests
import json
import plotly.express as px
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# --- 1. SETUP ---
analyzer = SentimentIntensityAnalyzer()

# SECURITY: Try to get from secrets, fallback to a placeholder
try:
    SERPER_API_KEY = st.secrets["SERPER_KEY"]
except:
    SERPER_API_KEY = "768f5110358df3687ff28972c9ab20fd25e73fd5"

def analyze_text(text):
    score = analyzer.polarity_scores(text)['compound']
    if score <= -0.05: return "🔴 HIGH", score
    elif score >= 0.05: return "🟢 LOW", score
    else: return "🟡 NEUTRAL", score

# --- 2. THE API FUNCTION ---
def get_vendor_data_api(vendor_name):
    url = "https://serper.dev"
    payload = json.dumps({"q": f"{vendor_name} complaints reviews", "num": 5})
    headers = {'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'}

    try:
        response = requests.post(url, headers=headers, data=payload)
        # Check if the API key is actually working
        if response.status_code == 403:
            return "Error: Invalid API Key. Check your Serper.dev dashboard."
        
        data = response.json()
        snippets = []
        if 'organic' in data:
            for result in data['organic']:
                snippets.append(result.get('snippet', ''))
        
        return " | ".join(snippets) if snippets else "No public data found."
    except Exception as e:
        return f"Connection Error: {str(e)}"

# --- 3. UI ---
st.set_page_config(page_title="Reputation Guard Pro", layout="wide")
st.title("Reputational Risk Dashboard 🛡️")

# Sidebar
st.sidebar.header("Settings")
uploaded_file = st.sidebar.file_uploader("Upload Vendor CSV", type=["csv"])

# Load Data
try:
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_csv("vendors.csv")
except:
    df = pd.DataFrame({"vendor_name": ["Example Firm A", "Example Firm B"]})

# --- 4. EXECUTION ---
if st.button("Launch Professional Audit"):
    results = []
    combined_text = ""
    
    with st.spinner("Accessing global search data..."):
        for index, row in df.iterrows():
            name = row['vendor_name']
            raw_text = get_vendor_data_api(name)
            combined_text += " " + raw_text
            
            risk_label, score = analyze_text(raw_text)
            results.append({
                "Vendor": name, 
                "Risk": risk_label, 
                "Score": score, 
                "Findings": raw_text
            })

    # Create the dataframe immediately so visuals don't crash
    res_df = pd.DataFrame(results)
    
    # --- 5. DISPLAY ---
    st.success("Audit Complete!")
    
    # Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Audited", len(res_df))
    m2.metric("High Risk Flags", len(res_df[res_df['Risk'] == "🔴 HIGH"]))
    m3.metric("Avg Sentiment", round(res_df['Score'].mean(), 2))

    st.divider()

    # Visuals
    col_left, col_right = st.columns([1, 1.5])
    
    with col_left:
        st.subheader("Risk Mix")
        fig = px.pie(res_df, names='Risk', color='Risk',
                     color_discrete_map={'🔴 HIGH':'#ff4b4b', '🟢 LOW':'#00cc96', '🟡 NEUTRAL':'#636efa'})
        st.plotly_chart(fig, use_container_width=True)

        # Only show cloud if we have real data (not errors)
        if len(combined_text) > 50 and "Error" not in combined_text:
            st.subheader("Risk Keywords")
            wc = WordCloud(background_color="white", colormap="Reds").generate(combined_text)
            fig_wc, ax = plt.subplots()
            ax.imshow(wc, interpolation='bilinear')
            ax.axis("off")
            st.pyplot(fig_wc)

    with col_right:
        st.subheader("Detailed Audit Log")
        st.dataframe(res_df, use_container_width=True)
