import sys
from pathlib import Path

# Add root directory to path so we can import shared_utils
root_dir = Path(__file__).parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

import streamlit as st  # noqa: E402

import shared_utils  # noqa: E402

# ==========================================
# 1. CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Context & Tradecraft",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

con = shared_utils.get_db_connection()

# ==========================================
# 3. MAIN CONTENT
# ==========================================
st.title("📚 Tradecraft Wiki")
st.caption("Strategic Context & Operational Reference")

st.markdown("---")

# Tabs to match Application Flow
tab_ops, tab_intel = st.tabs(["⚔️ Operations (War Room / Dorks)", "🧠 Intelligence (DeepDark)"])

with tab_ops:
    st.markdown("### 🌍 The 2025 RaaS Threat Landscape")
    st.info("Context for: **War Room** & **Dork Generator**")
    
    # Executive Summary Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Global Incident Surge", "+45%", "YoY (2025)", help="Source: NordStellar")
    c2.metric("Dominant Actor", "Qilin", "700+ Attacks", help="Source: Industrial Cyber")
    c3.metric("Top Emerging Threat", "Scattered Lapsus$", "#1 Ranking", help="Source: SOCRadar")

    st.markdown("""
    #### **Strategic Overview**
    The 2025 cyber threat landscape has been defined by the industrialization 
    of "Ransomware Cartels" and a decisive shift toward **Pure Extortion**. 
    Global ransomware incidents have surged, driven by decentralized affiliate 
    networks that have often abandoned traditional encryption.
    
    #### **Key Threat Indicators**
    *   **Volume Surge**: Attacks reached record highs (>9,200 incidents), 
        fueled by fragmentation of major groups (LockBit/ALPHV fallout).
    *   **Operational Shifts**:
        *   **Triple Extortion**: Encryption + Data Leak + DDoS/Harassment.
        *   **Pure Extortion**: Zero encryption. Actors simply exfiltrate 
            data and demand random (bypassing EDR).
    
    ---
    #### **Dominant Actors (2025)**
    1.  **Qilin**: The most prolific operator (>700 attacks/yr), aggressively 
        targeting healthcare.
    2.  **Scattered Lapsus$ Hunters**: A hybrid alliance merging high-end 
        social engineering (SIM swapping) with RaaS infrastructure.
    3.  **RansomHub**: Leading volume by adopting a "franchise" model for 
        displaced affiliates.
    
    ---
    
    #### **🛡️ Defensive Context**
    **"Google Hacking"** remains a primary reconnaissance vector for IABs 
    (Initial Access Brokers).
    *   **Objective**: Find exposed SQL backups, configuration files 
        (`.env`), and open directories (`intitle:"index of"`).
    *   **Countermeasure**: Use the **Dork Generator** to audit your 
        perimeter.
    """)

with tab_intel:
    st.markdown("### 🧅 Dark Web Infrastructure")
    st.info("Context for: **DeepDark Intelligence**")
    
    st.markdown("""
    #### **Infrastructure Correlation**
    Ransomware groups require robust, anonymous infrastructure to survive 
    takedowns (like OpCronos). 
    
    **The DeepDark View** correlates three key assets:
    1.  **Leak Sites**: Public shaming blogs (sanity check for victim claims).
    2.  **Negotiation Portals**: Where the actual extortion happens 
        (often requires distinct Tor auth).
    3.  **Affiliate Panels**: Login pages for the malware operators.
    
    #### **Graph Theory vs. Reality**
    While often visualized as a "Graph", the raw intelligence is best consumed 
    as a **correlation matrix**. 
    *   **Nodes**: Threat Groups & Onion URLs.
    *   **Edges**: Validated uptime checks.
    
    *Verify these connections in the **DeepDark Intelligence** module.*
    """)

st.markdown("---")

# Citations Footer
with st.expander("📚 Citations & Data Sources (Verified 2025)"):
    citations = [
        ("Global Incident Surge (45%)", "https://nordstellar.com/blog/ransomware-statistics/"),
        ("Qilin Dominance", "https://industrialcyber.co/ransomware/qilin-ransomware-escalates-rapidly"
                           "-in-2025-targeting-critical-sectors-with-700-attacks-amid-ransomhub-shutdown/"),
        ("Top Threat Actors", "https://socradar.io/blog/top-10-ransomware-groups-2025/"),
        ("Victim Trends", "https://content.blackkite.com/ebook/2025-ransomware-report/"),
        ("Crypto & Profit Models", "https://go.chainalysis.com/2025-Crypto-Crime-Report.html"),
        ("Extortion Doctrines", "https://www.commvault.com/explore/ransomware-trends-and-strategies")
    ]
    for title, url in citations:
        st.markdown(f"* **{title}**: [Source]({url})")
