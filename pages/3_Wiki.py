import streamlit as st
import shared_utils
import duckdb

# ==========================================
# 1. CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Context & Tradecraft",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. SHARED INFRASTRUCTURE
# ==========================================
@st.cache_resource
def get_db_connection():
    try:
        token = st.secrets.get("MOTHERDUCK_TOKEN")
        if token:
            return duckdb.connect(f'md:?motherduck_token={token}')
        else:
            return duckdb.connect('ransomstat.duckdb', read_only=True)
    except Exception as e:
        return None

con = get_db_connection()
shared_utils.render_analyst_tools(con)

# ==========================================
# 3. MAIN CONTENT
# ==========================================
st.title("� Context & Tradecraft")
st.caption("Understanding the concepts behind the RansomStat CTI Platform.")

st.markdown("---")

# Use columns for a cleaner, magazine-style layout
col1, col2, col3 = st.columns(3)

with col1:
    st.header("1. Ransomware")
    st.subheader("& The RaaS Economy")
    st.info("Powering the **Threat Ticker**")
    
    st.markdown("""
    **Ransomware-as-a-Service (RaaS)**
    Modern ransomware is not just malware; it's a business model.
    
    *   **The Developers**: Write the malware (encryptor) and maintain the payment/leak sites. They take a 20-30% cut.
    *   **The Affiliates**: The "hackers" who break into networks and deploy the ransomware. They keep 70-80% of the ransom.
    
    **Double Extortion**
    Encryption alone is no longer enough. Groups now practice **Double Extortion**:
    1.  **Exfiltrate** sensitive data first.
    2.  **Encrypt** the network.
    3.  **Threaten** to leak the data on a public blog if payment isn't made.
    
    *The **Threat Ticker** in this app monitors these specific leak blogs for new victim postings.*
    """)

with col2:
    st.header("2. The Dark Web")
    st.subheader("& Hidden Services")
    st.info("Powering the **Intel Graph**")
    
    st.markdown("""
    **Tor & .onion Sites**
    Ransomware groups operate on the Tor network to maintain anonymity. Their websites end in `.onion` and cannot be accessed by normal browsers.
    
    **Infrastructure types:**
    *   **Leak Sites**: Public blogs listing victims (PR/Shaming).
    *   **Negotiation Portals**: Private chat rooms where victims talk to hackers.
    *   **Affiliate Panels**: Login pages for the hackers to generate malware.
    
    **Volatility**
    These sites frequently go offline due to DDoS attacks from rivals, law enforcement takedowns (like Operation Cronos), or bad coding.
    
    *The **DeepDark Intelligence** page visualizes the connections between these groups and their `.onion` infrastructure.*
    """)

with col3:
    st.header("3. Google Dorks")
    st.subheader("& OSINT")
    st.info("Powering the **Dork Generator**")
    
    st.markdown("""
    **Passive Reconnaissance**
    "Google Dorking" (or Google Hacking) is the use of advanced search operators to find security holes without sending a single packet to the target.
    
    **Common Operators:**
    *   `site:example.com`: Limit results to a specific domain.
    *   `filetype:pdf`: Find specific file types.
    *   `intitle:"index of"`: Find exposed directory listings.
    
    **The Danger**
    Attackers use dorks to find exposed passwords, configuration files, and SQL backups left on the public web.
    
    *The **Dork Generator** automates this process defensively, helping you find what you've accidentally exposed before they do.*
    """)

st.markdown("---")

# Footer Context
with st.expander("📚 Terminology Glossary"):
    st.table([
        {"Term": "IAB (Initial Access Broker)", "Definition": "A criminal who hacks a company solely to sell the access (VPN/RDP) to a ransomware affiliate."},
        {"Term": "C2 (Command & Control)", "Definition": "The server used by attackers to control malware remotely."},
        {"Term": "TTPs", "Definition": "Tactics, Techniques, and Procedures - the 'fingerprint' of a specific threat group."},
        {"Term": "OpSec", "Definition": "Operational Security - how attackers hide their tracks (or fail to)."}
    ])
