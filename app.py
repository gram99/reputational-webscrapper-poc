import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# 1. Initialize the Sentiment Analyzer
analyzer = SentimentIntensityAnalyzer()

def get_risk_level(text):
    """Calculates sentiment and assigns a Risk Level."""
    score = analyzer.polarity_scores(text)['compound']
    if score <= -0.05:
        return "🔴 HIGH RISK", score
    elif score >= 0.05:
        return "🟢 LOW RISK", score
    else:
        return "🟡 NEUTRAL", score

# 2. Setup Headless Chrome Driver
def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), 
        options=chrome_options
    )

# 3. Streamlit Interface
st.set_page_config(page_title="Reputation Guard POC", layout="wide")
st.title("Reputational Risk Monitor 🛡️")
st.subheader("Law Firm & Vendor Compliance Check")

vendor_name = st.text_input("Enter Vendor Name:", placeholder="e.g., Smith & Associates Collections")

if st.button("Analyze Reputation"):
    if vendor_name:
        with st.spinner(f"Scraping and analyzing sentiment for {vendor_name}..."):
            try:
                # --- START SCRAPER ---
                driver = get_driver()
                
                # For this POC, we are simulating finding a review or news snippet
                # In a real tool, you'd use driver.find_elements to grab real text
                sample_found_text = f"Consumer reported that {vendor_name} used aggressive tactics and failed to provide debt validation letters."
                
                # --- ANALYZE SENTIMENT ---
                risk_label, raw_score = get_risk_level(sample_found_text)
                
                # --- DISPLAY RESULTS ---
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Reputation Status", risk_label)
                with col2:
                    st.metric("Sentiment Score", round(raw_score, 2))
                
                st.write("**Latest Scraped Content Highlight:**")
                st.info(sample_found_text)
                
                driver.quit()
                # --- END SCRAPER ---

            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Please enter a name to begin.")

# Sidebar for History or Instructions
st.sidebar.header("About this POC")
st.sidebar.write("This tool uses **Selenium** to gather public data and **VADER Sentiment** to flag potential reputational risks before hiring vendors.")
