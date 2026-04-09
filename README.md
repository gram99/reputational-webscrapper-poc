# 🛡️ Law Firm Reputation Auditor (PoC)

**📌 Project Overview:** This Proof of Concept (PoC) provides managers with a streamlined, automated dashboard to monitor the reputational risk of their legal vendor panels. By analyzing public sentiment and industry-specific red flags, this tool identifies which firms protect the firms's brand and which may pose a contractual or reputational threat.

## 🚀 Key Features

- **Automated Risk Tiering:** Instantly categorizes law firms into three actionable buckets:

  - 🟢 **Low Risk:** High professional standards; candidates for volume expansion.
  - 🟡 **Caution:** Mixed reviews; recommended for increased oversight/monitoring.
  - 🔴 **High Risk:** Significant consumer complaints; candidates for audit or termination.

- **Quantitative Scoring:** Assigns a Sentiment Risk Score (-1.0 to 1.0) to every firm for objective comparison across the panel.

- **Executive Dashboard:** High-level visual breakdown of the panel's "Risk Mix" via interactive Plotly charts.

- **Corporate-Safe Architecture:** Designed to run reliably behind corporate VPNs and firewalls without external API dependencies.

- **Standardized Workflow:** Includes a downloadable CSV template to ensure seamless data ingestion and user adoption.

---

## 🛠️ Technical Stack

- **Language:** Python 3.x

- **Interface:** Streamlit

- **Analysis Engine:** VADER Sentiment Analysis (Natural Language Processing - NLP)

- **Visualization:** Plotly Express

- **Data Handling:** Pandas

---

## 📋 How to Use

1. **Download Template:** Click the "Download CSV Template" button in the sidebar.

2. **Input Data:** Fill in your vendor names, cities, and states into the template.

3. **Upload & Audit:** Upload the completed file and click "Launch Professional Audit."

4. **Review & Export:** Analyze the dashboard and download the full "Compliance Audit Report" for internal records.

## 📈 Future Roadmap

- **V2.0:** Integration with internal Bank Vendor Management (VMS) databases.

- **V2.1:** Automated email alerts for sudden shifts in vendor risk scores.

- **V2.2:** Historical trend mapping to track reputation improvement/decline over time.

---

## Screen Shots

<img width="1896" height="801" alt="Screenshot 2026-04-08 at 9 02 06 PM" src="https://github.com/user-attachments/assets/4e5ba7d2-a4c1-41a7-83e1-e0a83e0fbc97" />


<img width="971" height="305" alt="Screenshot 2026-04-08 at 9 02 32 PM" src="https://github.com/user-attachments/assets/0ba65267-d958-492f-b4a1-ccc040a01781" />
