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
SERPER_API_KEY = "768f5110358df3687ff28972c9ab20fd25e73fd5"

def analyze_text(text):
    score = analyzer.polarity_scores(text)['compound']
    if score <= -0.05: return "🔴 HIGH", score
    elif score >= 0.05: return "🟢 LOW", score
    else: return "🟡 NEUTRAL", score

# --- 2. THE NEW SEARCH FUNCTION (NO SELENIUM!) ---
def get_vendor_data_api(vendor_name):
    url = "https://serper.dev"
    
    # We ask for news and general results for "vendor name complaints"
    payload = json.dumps({
        "q": f"{vendor_name} complaints reviews",
        "num": 5
    })
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        data = response.json()
        
        # We grab snippets from the search results
        snippets = []
        if 'organic' in data:
            for result in data['organic'][:3]:
                snippets.append(result.get('snippet', ''))
        
        return " | ".join(snippets) if snippets else "No public data found."
    except Exception as e:
        return f"API Error: {str(e)}"

# --- 3. UI ---
st.set_page_config(page_title="Reputation Guard Pro", layout="wide")
st.title("Reputational Risk Executive Dashboard 🛡️")

st.sidebar.header("Data Management")
uploaded_file = st.sidebar.file_uploader("Upload Vendor CSV", type=["csv"])

if not uploaded_file:
    try:
        df = pd.read_csv("vendors.csv")
    except:
        df = pd.DataFrame(columns=["vendor_name"])
else:
    df = pd.read_csv(uploaded_file)

# --- 4. EXECUTION ---
if st.button("Launch Professional Reputation Audit") and not df.empty:
    results = []
    all_text_for_cloud = ""
    
    # Notice: No 'driver' needed anymore! 
    # It runs much faster so we don't need long progress bars.
    with st.spinner("Analyzing vendor panel..."):
        for index, row in df.iterrows():
            name = row['vendor_name']
            
            # API call is near-instant
            real_text = get_vendor_data_api(name)
            all_text_for_cloud += " " + real_text
            
            risk_label, score = analyze_text(real_text)
            results.append({
                "Vendor": name, 
                "Risk": risk_label, 
                "Score": score, 
                "Search Snippets": real_text
            })
    
    # --- 5. RESULTS ---
    st.success("Audit Complete!")
    res_df = pd.DataFrame(results)

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Vendors Checked", len(res_df))
    c2.metric("High Risk Flags", len(res_df[res_df['Risk'] == "🔴 HIGH"]))
    c3.metric("Avg Sentiment Score", round(res_df['Score'].mean(), 2))

    st.divider()

    col_chart, col_table = st.columns([1, 1.5])
    
    with col_chart:
        st.subheader("Reputation Distribution")
        fig_pie = px.pie(res_df, names='Risk', color='Risk',
                     color_discrete_map={'🔴 HIGH':'#ff4b4b', '🟢 LOW':'#00cc96', '🟡 NEUTRAL':'#636efa'})
        st.plotly_chart(fig_pie, use_container_width=True)

        if all_text_for_cloud.strip():
            st.subheader("Key Risk Keywords")
            wc = WordCloud(width=400, height=200, background_color='white', colormap='Reds').generate(all_text_for_cloud)
            fig_wc, ax = plt.subplots()
            ax.imshow(wc, interpolation='bilinear')
            ax.axis("off")
            st.pyplot(fig_wc)

    with table_col:
        st.subheader("Findings & Live Sources")
        st.dataframe(res_df, use_container_width=True)

    csv_report = res_df.to_csv(index=False).encode('utf-8')
    st.download_button("📩 Download Compliance Audit Report", data=csv_report, file_name="reputation_audit_report.csv")
