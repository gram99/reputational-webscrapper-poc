import streamlit as st
import pandas as pd
import requests

# --- 1. SETUP ---
# Replace with your actual key directly for this test
API_KEY = "d8d5cbf1dc92ecc4fba5b9154763c8243cd7910d" 

def get_search_results(vendor_name):
    """Simplified search function focusing only on data retrieval."""
    url = f"https://serper.dev{vendor_name}+complaints"
    headers = {'X-API-KEY': API_KEY}
    
    try:
        # Using a simple GET request instead of a complex POST
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Grab just the first snippet to prove it works
            if 'organic' in data and len(data['organic']) > 0:
                return data['organic'][0].get('snippet', 'Data found, but no snippet.')
            return "Search successful, but no public complaints found."
        else:
            return f"Server Error: {response.status_code}"
    except Exception as e:
        return f"Connection Issue: {str(e)[:50]}"

# --- 2. SIMPLE UI ---
st.title("Reputational Risk Scraper POC 🛡️")

# Load your vendors.csv
try:
    df = pd.read_csv("vendors.csv")
    st.write("### Current Vendor List", df)
except:
    st.error("Could not find vendors.csv. Please ensure it is in your GitHub repo.")
    df = pd.DataFrame()

if st.button("Run Scraper") and not df.empty:
    results = []
    
    with st.spinner("Fetching live data..."):
        for index, row in df.iterrows():
            name = row['vendor_name']
            # Get the raw data
            findings = get_search_results(name)
            results.append({"Vendor": name, "Public Findings": findings})
            
    # Display simple results table
    res_df = pd.DataFrame(results)
    st.success("Scrape Complete!")
    st.table(res_df)
